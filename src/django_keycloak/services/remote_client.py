import logging

from django.utils import timezone

from django_keycloak.models import ExchangedToken

import django_keycloak.services.oidc_profile


logger = logging.getLogger(__name__)


def exchange_token(oidc_profile, remote_client):
    """
    Exchange access token from OpenID Connect profile for a token of given
    remote client.

    :param django_keycloak.models.OpenIdConnectProfile oidc_profile:
    :param django_keycloak.models.RemoteClient remote_client:
    :rtype: dict
    """
    active_access_token = django_keycloak.services.oidc_profile\
        .get_active_access_token(oidc_profile=oidc_profile)

    # http://www.keycloak.org/docs/latest/securing_apps/index.html#_token-exchange
    return oidc_profile.realm.client.openid_api_client.token_exchange(
        audience=remote_client.name,
        subject_token=active_access_token,
        requested_token_type='urn:ietf:params:oauth:token-type:refresh_token'
    )


def get_active_remote_client_token(oidc_profile, remote_client):
    """
    Get an active remote client token. Exchange when not available or expired.

    :param django_keycloak.models.OpenIdConnectProfile oidc_profile:
    :param django_keycloak.models.RemoteClient remote_client:
    :rtype: str
    """
    exchanged_token, _ = ExchangedToken.objects.get_or_create(
        oidc_profile=oidc_profile,
        remote_client=remote_client
    )

    initiate_time = timezone.now()

    if exchanged_token.refresh_expires_before is None \
            or initiate_time > exchanged_token.refresh_expires_before \
            or initiate_time > exchanged_token.expires_before:
        token_response = exchange_token(oidc_profile, remote_client)

        exchanged_token = django_keycloak.services.oidc_profile.update_tokens(
            token_model=exchanged_token,
            token_response=token_response,
            initiate_time=initiate_time
        )

    return exchanged_token.access_token
