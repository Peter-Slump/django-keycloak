import logging

from functools import partial

from django.utils import timezone

from django_keycloak.services.exceptions import TokensExpired

import django_keycloak.services.oidc_profile


logger = logging.getLogger(__name__)


def get_keycloak_id(client):
    """
    Get internal Keycloak id for client configured in Realm
    :param django_keycloak.models.Realm realm:
    :return:
    """
    keycloak_clients = client.admin_api_client.realms.by_name(
        name=client.realm.name).clients.all()
    for keycloak_client in keycloak_clients:
        if keycloak_client['clientId'] == client.client_id:
            return keycloak_client['id']

    return None


def get_authz_api_client(client):
    """
    :param django_keycloak.models.Client client:
    :rtype: keycloak.authz.KeycloakAuthz
    """
    return client.realm.realm_api_client.authz(client_id=client.client_id)


def get_openid_client(client):
    """
    :param django_keycloak.models.Client client:
    :rtype: keycloak.openid_connect.KeycloakOpenidConnect
    """
    openid = client.realm.realm_api_client.open_id_connect(
        client_id=client.client_id,
        client_secret=client.secret
    )

    if client.realm._well_known_oidc:
        openid.well_known.contents = client.realm.well_known_oidc

    return openid


def get_uma1_client(client):
    """
    :type client: django_keycloak.models.Client
    :rtype: keycloak.uma1.KeycloakUMA1
    """
    return client.realm.realm_api_client.uma1


def get_admin_client(client):
    """
    Get the Keycloak admin client configured for given realm.

    :param django_keycloak.models.Client client:
    :rtype: keycloak.admin.KeycloakAdmin
    """
    token = partial(get_access_token, client)
    return client.realm.realm_api_client.admin.set_token(token=token)


def get_service_account_profile(client):
    """
    Get service account for given client.

    :param django_keycloak.models.Client client:
    :rtype: django_keycloak.models.OpenIdConnectProfile
    """

    if client.service_account_profile:
        return client.service_account_profile

    token_response, initiate_time = get_new_access_token(client=client)

    oidc_profile = django_keycloak.services.oidc_profile._update_or_create(
        client=client,
        token_response=token_response,
        initiate_time=initiate_time)

    client.service_account_profile = oidc_profile
    client.save(update_fields=['service_account_profile'])

    return oidc_profile


def get_new_access_token(client):
    """
    Get client access_token

    :param django_keycloak.models.Client client:
    :rtype: str
    """
    scope = 'realm-management openid'

    initiate_time = timezone.now()
    token_response = client.openid_api_client.client_credentials(scope=scope)

    return token_response, initiate_time


def get_access_token(client):
    """
    Get access token from client's service account.
    :param django_keycloak.models.Client client:
    :rtype: str
    """

    oidc_profile = get_service_account_profile(client=client)

    try:
        return django_keycloak.services.oidc_profile.get_active_access_token(
            oidc_profile=oidc_profile)
    except TokensExpired:
        token_reponse, initiate_time = get_new_access_token(client=client)
        oidc_profile = django_keycloak.services.oidc_profile.update_tokens(
            token_model=oidc_profile,
            token_response=token_reponse,
            initiate_time=initiate_time
        )
        return oidc_profile.access_token
