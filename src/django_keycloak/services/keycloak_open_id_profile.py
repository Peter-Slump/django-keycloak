from datetime import timedelta

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from keycloak.exceptions import KeycloakClientError

from django_keycloak.remote_user import KeycloakRemoteUser


logger = logging.getLogger(__name__)


def get_remote_user_model():
    """
    Return the User model that is active in this project.
    """
    if not hasattr(settings, 'AUTH_REMOTE_USER_MODEL'):
        # By default return the standard KeycloakRemoteUser model
        return KeycloakRemoteUser

    try:
        return import_string(settings.AUTH_REMOTE_USER_MODEL)
    except ImportError:
        raise ImproperlyConfigured(
            "AUTH_REMOTE_USER_MODEL refers to non-existing class"
        )


def update_or_create(realm, code, redirect_uri):
    """
    Update or create an KeycloakOpenIdProfile based on the Access Token
    Response as specified in:

    https://tools.ietf.org/html/rfc6749#section-4.1.4

    :param django_keycloak.models.Realm realm:
    :param str code: authentication code
    :rtype: django_keycloak.models.KeycloakOpenIDProfile
    """

    now = timezone.now()
    response_dict = realm.keycloak_openid.authorization_code(
        code=code, redirect_uri=redirect_uri)

    id_token_object = realm.keycloak_openid.decode_token(
        token=response_dict['id_token'],
        key=realm.certs,
        algorithms=realm.keycloak_openid.well_known[
            'id_token_signing_alg_values_supported']
    )

    expires_before = now + timedelta(seconds=response_dict['expires_in'])
    refresh_expires_before = now + timedelta(
        seconds=response_dict['refresh_expires_in'])

    keycloak_profile, created = realm.openid_profiles.get_or_create(
        sub=id_token_object['sub']
    )

    # Updating with new tokens
    keycloak_profile.access_token = response_dict['access_token']
    keycloak_profile.expires_before = expires_before
    keycloak_profile.refresh_token = response_dict['refresh_token']
    keycloak_profile.refresh_expires_before = refresh_expires_before
    keycloak_profile.save(update_fields=['access_token', 'expires_before',
                                         'refresh_token',
                                         'refresh_expires_before'])

    if not hasattr(settings, 'AUTH_REMOTE_USER_MODEL'):
        get_or_create_user_from_profile(oidc_profile=keycloak_profile)

    return keycloak_profile


def get_active_access_token(oidc_profile):
    """
    Give access_token and refresh when required.

    :param django_keycloak.models.KeycloakOpenIDProfile openid_profile:
    :rtype: string
    """
    now = timezone.now()

    if now > oidc_profile.expires_before:
        # Refresh token
        new_token = oidc_profile.realm.keycloak_openid.refresh_token(
            refresh_token=oidc_profile.refresh_token)

        oidc_profile.access_token = new_token['access_token']
        oidc_profile.expires_before = now + timedelta(
            seconds=new_token['expires_in'])
        oidc_profile.refresh_token = new_token['refresh_token']
        oidc_profile.refresh_expires_before = now + timedelta(
            seconds=new_token['refresh_expires_in'])

        oidc_profile.save(update_fields=['access_token', 'expires_before',
                                         'refresh_token',
                                         'refresh_expires_before'])

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

    rpt = oidc_profile.realm.authz.entitlement(token=access_token)

    rpt_decoded = oidc_profile.realm.keycloak_openid.decode_token(
        token=rpt['rpt'],
        key=oidc_profile.realm.certs,
        options={
            'verify_signature': True,
            'exp': True,
            'iat': True,
            'aud': True
        })
    logger.debug('get_keycloak_permissions %s', rpt_decoded)
    return rpt_decoded


def get_or_create_user_from_profile(oidc_profile):
    """

    :param oidc_profile:
    :return:
    """

    UserModel = get_user_model()

    userinfo = oidc_profile.realm.keycloak_openid.userinfo(
        token=oidc_profile.access_token
    )

    try:
        user = oidc_profile.user
    except UserModel.DoesNotExist:
        user = UserModel()
        user.username = oidc_profile.sub
        user.oidc_profile = oidc_profile
        user.set_unusable_password()

    user.email = userinfo.get('email', '')
    user.first_name = userinfo.get('given_name', '')
    user.last_name = userinfo.get('family_name', '')
    user.save()

    return user


def get_remote_user_from_profile(oidc_profile):
    """

    :param oidc_profile:
    :return:
    """

    try:
        userinfo = oidc_profile.realm.keycloak_openid.userinfo(
            token=oidc_profile.access_token
        )
    except KeycloakClientError:
        return None

    # Get the user from the AUTH_REMOTE_USER_MODEL in the settings
    UserModel = get_remote_user_model()

    # Create the object of type UserModel from the constructor of it's class as the included details can vary per model
    user = UserModel(userinfo, oidc_profile)

    return user
