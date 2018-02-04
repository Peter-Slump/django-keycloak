from datetime import timedelta

import json

from django.utils import timezone
from keycloak.realm import KeycloakRealm
from keycloak.well_known import KeycloakWellKnown

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
    well_known = None
    if realm.well_known:
        well_known = KeycloakWellKnown(content=realm.well_known)

    return realm.keycloak_realm.open_id_connect(
        client_id=realm.client_id,
        client_secret=realm.client_secret,
        well_known=well_known
    )


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
    return realm.keycloak_realm.uma()


def refresh_certs(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    keycloak_openid = realm.keycloak_openid

    certs = keycloak_openid.certs()

    realm.certs = json.dumps(certs)
    realm.save(update_fields=['certs'])
    return realm


def refresh_well_known(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    keycloak_openid = realm.keycloak_openid

    well_known = keycloak_openid.well_known

    realm.well_known = json.dumps(well_known.contents)
    realm.save(update_fields=['well_known'])
    return realm


def get_access_token(realm):
    """
    Get client access_token

    :param django_keycloak.models.Realm realm:
    :rtype: str
    """
    token = None
    scope = 'uma_protection'

    now = timezone.now()
    if realm.access_token is None or realm.refresh_expires_before < now:
        token = realm.keycloak_openid.client_credentials(scope=scope)
    elif realm.expires_before < now:
        token = realm.keycloak_openid.refresh_token(
            refresh_token=realm.refresh_token,
            scope=scope
        )

    if token:
        realm.access_token = token['access_token']
        realm.expires_before = now + timedelta(seconds=token['expires_in'])
        realm.refresh_token = token['refresh_token']
        realm.refresh_expires_before = now + timedelta(
            seconds=token['refresh_expires_in'])

        realm.save(update_fields=['access_token', 'expires_before',
                                  'refresh_token', 'refresh_expires_before'])

    return realm.access_token
