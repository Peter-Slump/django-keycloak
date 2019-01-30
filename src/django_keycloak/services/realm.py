from keycloak.realm import KeycloakRealm

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def get_realm_api_client(realm):
    """
    :param django_keycloak.models.Realm realm:
    :return keycloak.realm.Realm:
    """
    headers = {}
    server_url = realm.server.url
    if realm.server.internal_url:
        # An internal URL is configured. We add some additional settings to let
        # Keycloak think that we access it using the server_url.
        server_url = realm.server.internal_url
        parsed_url = urlparse(realm.server.url)
        headers['Host'] = parsed_url.netloc

        if parsed_url.scheme == 'https':
            headers['X-Forwarded-Proto'] = 'https'

    return KeycloakRealm(server_url=server_url, realm_name=realm.name,
                         headers=headers)


def refresh_certs(realm):
    """
    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    realm.certs = realm.client.openid_api_client.certs()
    realm.save(update_fields=['_certs'])
    return realm


def refresh_well_known_oidc(realm):
    """
    Refresh Open ID Connect .well-known

    :param django_keycloak.models.Realm realm:
    :rtype django_keycloak.models.Realm
    """
    server_url = realm.server.internal_url or realm.server.url

    # While fetching the well_known we should not use the prepared URL
    openid_api_client = KeycloakRealm(
        server_url=server_url,
        realm_name=realm.name
    ).open_id_connect(client_id='', client_secret='')

    realm.well_known_oidc = openid_api_client.well_known.contents
    realm.save(update_fields=['_well_known_oidc'])
    return realm


def get_issuer(realm):
    """
    Get correct issuer to validate the JWT against. If an internal URL is
    configured for the server it will be replaced with the public one.

    :param django_keycloak.models.Realm realm:
    :return: issuer
    :rtype: str
    """
    issuer = realm.well_known_oidc['issuer']
    if realm.server.internal_url:
        return issuer.replace(realm.server.internal_url, realm.server.url, 1)
    return issuer
