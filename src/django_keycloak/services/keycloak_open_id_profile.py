from datetime import timedelta

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone

from django_keycloak.models import KeycloakOpenIDProfile


logger = logging.getLogger(__name__)


def update_or_create(realm, code, redirect_uri):
    """
    Update or create an KeycloakOpenIdProfile based on the Access Token
    Response as specified in:

    https://tools.ietf.org/html/rfc6749#section-4.1.4

    :param django_keycloak.models.Realm realm:
    :param str code: authentication code
    :rtype: django_keycloak.models.KeycloakOpenIDProfile
    """
    now = timezone.now()  # Define "now" before getting the access token.
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

    userinfo = realm.keycloak_openid.userinfo(
        token=response_dict['access_token'])

    try:
        keycloak_profile = realm.openid_profiles.get(
            sub=id_token_object['sub'])

        # Updating with new tokens
        keycloak_profile.access_token = response_dict['access_token']
        keycloak_profile.expires_before = expires_before
        keycloak_profile.refresh_token = response_dict['refresh_token']
        keycloak_profile.refresh_expires_before = refresh_expires_before
        keycloak_profile.save(update_fields=['access_token',
                                             'expires_before',
                                             'refresh_token',
                                             'refresh_expires_before'])

        logger.debug('KeycloakOpenIDProfile found, sub %s' %
                     id_token_object['sub'])

        user = keycloak_profile.user
        user.email = userinfo.get('email', '')
        user.first_name = userinfo.get('given_name', '')
        user.last_name = userinfo.get('family_name', '')
        user.save(update_fields=['email', 'first_name', 'last_name'])

        return keycloak_profile
    except KeycloakOpenIDProfile.DoesNotExist:
        logger.debug("KeycloakOpenIDProfile for sub %s not found, so it'll be "
                     "created" % id_token_object['sub'])

    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(username=id_token_object['sub'])
    except UserModel.DoesNotExist:
        user = UserModel()
        user.username = id_token_object['sub']
        user.set_unusable_password()

    user.email = userinfo.get('email', '')
    user.first_name = userinfo.get('given_name', '')
    user.last_name = userinfo.get('family_name', '')
    user.save()

    return realm.openid_profiles.create(
        sub=id_token_object['sub'],
        user=user,
        access_token=response_dict['access_token'],
        expires_before=expires_before,
        refresh_token=response_dict['refresh_token'],
        refresh_expires_before=refresh_expires_before
    )


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
