from datetime import timedelta
from functools import partial

from django.utils import timezone
from requests.exceptions import HTTPError
from keycloak.realm import KeycloakRealm

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def get_keycloak_realm(realm):
    """
    :param django_keycloak.models.Realm realm:
    :return keycloak.realm.Realm:
    """
    headers = {}
    server_url = realm.server_url
    if realm.internal_server_url is not None:
        # An internal URL is configured. We add some additional settings to let
        # Keycloak think that we access it using the server_url.
        server_url = realm.internal_server_url
        parsed_url = urlparse(realm.server_url)
        headers['Host'] = parsed_url.netloc

        if parsed_url.scheme == 'https':
            headers['X-Forwarded-Proto'] = 'https'

    return KeycloakRealm(server_url=server_url, realm_name=realm.name,
                         headers=headers)


def get_keycloak_openid(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype: keycloak.openid_connect.KeycloakOpenidConnect
    """
    openid = realm.keycloak_realm.open_id_connect(
        client_id=realm.client_id,
        client_secret=realm.client_secret
    )

    if realm._well_known_oidc:
        openid.well_known.contents = realm.well_known_oidc

    return openid


def get_keycloak_authz(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype: keycloak.authz.KeycloakAuthz
    """
    return realm.keycloak_realm.authz(client_id=realm.client_id)


def get_keycloak_uma(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype: keycloak.authz.KeycloakUMA
    """
    uma = realm.keycloak_realm.uma()

    if realm._well_known_uma:
        uma.well_known.contents = realm.well_known_uma

    return uma


def refresh_certs(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    keycloak_openid = realm.keycloak_openid

    realm.certs = keycloak_openid.certs()
    realm.save(update_fields=['_certs'])
    return realm


def refresh_well_known_oidc(realm):
    """
    Refresh Open ID Connect .well-known

    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    if realm.internal_server_url:
        # While fetching the well_known we should not use the prepared URL
        keycloak_openid = KeycloakRealm(
            server_url=realm.internal_server_url,
            realm_name=realm.name
        ).open_id_connect(
            client_id=realm.client_id,
            client_secret=realm.client_secret
        )
    else:
        keycloak_openid = realm.keycloak_openid

    well_known = keycloak_openid.well_known

    realm.well_known_oidc = well_known.contents
    realm.save(update_fields=['_well_known_oidc'])
    return realm


def refresh_well_known_uma(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    if realm.internal_server_url:
        # While fetching the well_known we should not use the prepared URL
        keycloak_uma = KeycloakRealm(
            server_url=realm.internal_server_url,
            realm_name=realm.name
        ).uma()
    else:
        keycloak_uma = realm.uma()

    well_known = keycloak_uma.well_known

    realm.well_known_uma = well_known.contents
    realm.save(update_fields=['_well_known_uma'])
    return realm


def get_access_token(realm):
    """
    Get client access_token

    :param django_keycloak.models.Realm realm:
    :rtype: str
    """
    token = None
    scope = 'uma_protection realm-management'

    now = timezone.now()
    if realm.access_token is None or realm.refresh_expires_before < now:
        token = realm.keycloak_openid.client_credentials(scope=scope)
    elif realm.expires_before < now:
        try:
            token = realm.keycloak_openid.refresh_token(
                refresh_token=realm.refresh_token,
                scope=scope
            )
        except HTTPError as e:
            if e.response.json().get('code') == 'invalid_grant':
                token = realm.keycloak_openid.client_credentials(scope=scope)

    if token:
        realm.access_token = token['access_token']
        realm.expires_before = now + timedelta(seconds=token['expires_in'])
        realm.refresh_token = token['refresh_token']
        realm.refresh_expires_before = now + timedelta(
            seconds=token['refresh_expires_in'])

        realm.save(update_fields=['access_token', 'expires_before',
                                  'refresh_token', 'refresh_expires_before'])

    return realm.access_token


def get_admin_client(realm):
    """
    Get the Keycloak admin client configured for given realm.

    :param django_keycloak.models.Realm realm:
    :rtype: keycloak.admin.KeycloakAdmin
    """
    token = partial(get_access_token, realm)
    return realm.keycloak_realm.admin.set_token(token=token)
