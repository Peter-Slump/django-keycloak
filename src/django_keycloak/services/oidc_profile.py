from datetime import timedelta

import logging

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.module_loading import import_string
from keycloak.exceptions import KeycloakClientError

from django_keycloak.services.exceptions import TokensExpired
from django_keycloak.remote_user import KeycloakRemoteUser


import django_keycloak.services.realm

logger = logging.getLogger(__name__)


def get_openid_connect_profile_model():
    """
    Return the OpenIdConnectProfile model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.KEYCLOAK_OIDC_PROFILE_MODEL,
                                     require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "KEYCLOAK_OIDC_PROFILE_MODEL must be of the form "
            "'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "KEYCLOAK_OIDC_PROFILE_MODEL refers to model '%s' that has not "
            "been installed" % settings.KEYCLOAK_OIDC_PROFILE_MODEL)


def get_remote_user_model():
    """
    Return the User model that is active in this project.
    """
    if not hasattr(settings, 'KEYCLOAK_REMOTE_USER_MODEL'):
        # By default return the standard KeycloakRemoteUser model
        return KeycloakRemoteUser

    try:
        return import_string(settings.KEYCLOAK_REMOTE_USER_MODEL)
    except ImportError:
        raise ImproperlyConfigured(
            "KEYCLOAK_REMOTE_USER_MODEL refers to non-existing class"
        )


def get_or_create_from_id_token(client, id_token):
    """
    Get or create OpenID Connect profile from given id_token.

    :param django_keycloak.models.Client client:
    :param str id_token:
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """
    issuer = django_keycloak.services.realm.get_issuer(client.realm)

    id_token_object = client.openid_api_client.decode_token(
        token=id_token,
        key=client.realm.certs,
        algorithms=client.openid_api_client.well_known[
            'id_token_signing_alg_values_supported'],
        issuer=issuer
    )

    return update_or_create_user_and_oidc_profile(
        client=client, id_token_object=id_token_object)


def update_or_create_user_and_oidc_profile(client, id_token_object):
    """

    :param client:
    :param id_token_object:
    :return:
    """

    OpenIdConnectProfileModel = get_openid_connect_profile_model()

    if OpenIdConnectProfileModel.is_remote:
        oidc_profile, _ = OpenIdConnectProfileModel.objects.\
            update_or_create(
                sub=id_token_object['sub'],
                defaults={
                    'realm': client.realm
                }
            )

        UserModel = get_remote_user_model()
        oidc_profile.user = UserModel(id_token_object)

        return oidc_profile

    with transaction.atomic():
        UserModel = get_user_model()
        email_field_name = UserModel.get_email_field_name()
        user, _ = UserModel.objects.update_or_create(
            username=id_token_object['preferred_username'], # modified to map with the username
            defaults={
                email_field_name: id_token_object.get('email', ''),
                'first_name': id_token_object.get('given_name', ''),
                'last_name': id_token_object.get('family_name', '')
            }
        )

        oidc_profile, _ = OpenIdConnectProfileModel.objects.update_or_create(
            sub=id_token_object['sub'],
            defaults={
                'realm': client.realm,
                'user': user
            }
        )

    return oidc_profile


def get_remote_user_from_profile(oidc_profile):
    """

    :param oidc_profile:
    :return:
    """

    try:
        userinfo = oidc_profile.realm.client.openid_api_client.userinfo(
            token=oidc_profile.access_token
        )
    except KeycloakClientError:
        return None

    # Get the user from the KEYCLOAK_REMOTE_USER_MODEL in the settings
    UserModel = get_remote_user_model()

    # Create the object of type UserModel from the constructor of it's class
    # as the included details can vary per model
    user = UserModel(userinfo)

    return user


def update_or_create_from_code(code, client, redirect_uri):
    """
    Update or create an user based on an authentication code.
    Response as specified in:

    https://tools.ietf.org/html/rfc6749#section-4.1.4

    :param django_keycloak.models.Client client:
    :param str code: authentication code
    :param str redirect_uri
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """

    # Define "initiate_time" before getting the access token to calculate
    # before which time it expires.
    initiate_time = timezone.now()
    token_response = client.openid_api_client.authorization_code(
        code=code, redirect_uri=redirect_uri)

    return _update_or_create(client=client, token_response=token_response,
                              initiate_time=initiate_time)


def update_or_create_from_password_credentials(username, password, client):
    """
    Update or create an user based on username and password.
    Response as specified in:

    https://tools.ietf.org/html/rfc6749#section-4.3.3

    :param str username: the username to authenticate with
    :param str password: the password to authenticate with
    :param django_keycloak.models.Client client:
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """

    # Define "initiate_time" before getting the access token to calculate
    # before which time it expires.
    initiate_time = timezone.now()
    token_response = client.openid_api_client.password_credentials(
        username=username, password=password)

    return _update_or_create(client=client, token_response=token_response,
                             initiate_time=initiate_time)


def _update_or_create(client, token_response, initiate_time):
    """
    Update or create an user based on a token response.

    `token_response` contains the items returned by the OpenIDConnect Token API
    end-point:
     - id_token
     - access_token
     - expires_in
     - refresh_token
     - refresh_expires_in

    :param django_keycloak.models.Client client:
    :param dict token_response:
    :param datetime.datetime initiate_time:
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """
    issuer = django_keycloak.services.realm.get_issuer(client.realm)

    token_response_key = 'id_token' if 'id_token' in token_response \
        else 'access_token'

    token_object = client.openid_api_client.decode_token(
        token=token_response[token_response_key],
        key=client.realm.certs,
        algorithms=client.openid_api_client.well_known[
            'id_token_signing_alg_values_supported'],
        issuer=issuer,
        access_token=token_response["access_token"], # modified to fix the issue https://github.com/Peter-Slump/django-keycloak/issues/57
    )

    oidc_profile = update_or_create_user_and_oidc_profile(
        client=client,
        id_token_object=token_object)

    return update_tokens(token_model=oidc_profile,
                         token_response=token_response,
                         initiate_time=initiate_time)


def update_tokens(token_model, token_response, initiate_time):
    """
    Update tokens on the OpenID Connect profile

    :param django_keycloak.models.TokenModelAbstract token_model:
    :param dict token_response: response from OIDC token API end-point
    :param datetime.datetime initiate_time: timestamp before the token request
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """
    expires_before = initiate_time + timedelta(
        seconds=token_response['expires_in'])
    refresh_expires_before = initiate_time + timedelta(
        seconds=token_response['refresh_expires_in'])

    token_model.access_token = token_response['access_token']
    token_model.expires_before = expires_before
    token_model.refresh_token = token_response['refresh_token']
    token_model.refresh_expires_before = refresh_expires_before

    token_model.save(update_fields=['access_token',
                                    'expires_before',
                                    'refresh_token',
                                    'refresh_expires_before'])
    return token_model


def get_active_access_token(oidc_profile):
    """
    Give access_token and refresh when required.

    :param django_keycloak.models.KeycloakOpenIDProfile openid_profile:
    :rtype: string
    :raise: django_keycloak.services.exceptions.TokensExpired
    """
    initiate_time = timezone.now()

    if oidc_profile.refresh_expires_before is None \
            or initiate_time > oidc_profile.refresh_expires_before:
        raise TokensExpired()

    if initiate_time > oidc_profile.expires_before:
        # Refresh token
        token_response = oidc_profile.realm.client.openid_api_client\
            .refresh_token(refresh_token=oidc_profile.refresh_token)

        oidc_profile = update_tokens(token_model=oidc_profile,
                                     token_response=token_response,
                                     initiate_time=initiate_time)

    return oidc_profile.access_token


def get_entitlement(oidc_profile):
    """
    Get entitlement.

    http://www.keycloak.org/docs/latest/authorization_services/index.html#_service_entitlement_api

    :param django_keycloak.models.KeycloakOpenIDProfile oidc_profile:
    :rtype: dict
    :return: Decoded RPT
    """
    access_token = get_active_access_token(oidc_profile=oidc_profile)

    rpt = oidc_profile.realm.client.authz_api_client.entitlement(
        token=access_token)

    rpt_decoded = oidc_profile.realm.client.openid_api_client.decode_token(
        token=rpt['rpt'],
        key=oidc_profile.realm.certs,
        options={
            'verify_signature': True,
            'exp': True,
            'iat': True,
            'aud': True
        })
    return rpt_decoded


def get_decoded_jwt(oidc_profile):
    """
    :param django_keycloak.models.KeycloakOpenIDProfile oidc_profile:
    :rtype dict
    """

    client = oidc_profile.realm.client

    active_access_token = get_active_access_token(oidc_profile=oidc_profile)

    return client.openid_api_client.decode_token(
        token=active_access_token,
        key=client.realm.certs,
        algorithms=client.openid_api_client.well_known[
            'id_token_signing_alg_values_supported']
    )
