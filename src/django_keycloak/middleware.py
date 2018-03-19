import logging
import re

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from jose.exceptions import (
    ExpiredSignatureError,
    JWTClaimsError,
    JWTError,
)

from django_keycloak.models import Realm
from django_keycloak.response import HttpResponseNotAuthorized

import django_keycloak.services.oidc_profile

logger = logging.getLogger(__name__)


def get_realm(request):
    if not hasattr(request, '_cached_realm'):
        request._cached_realm = Realm.objects.first()
    return request._cached_realm


class BaseKeycloakMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """
        Adds Realm to request.
        :param request: django request
        """
        request.realm = SimpleLazyObject(lambda: get_realm(request))


class KeycloakBearerAuthenticationMiddleware(BaseKeycloakMiddleware):

    header = "HTTP_AUTHORIZATION"

    def process_request(self, request):
        super(KeycloakBearerAuthenticationMiddleware, self).process_request(
            request=request)

        if hasattr(settings, 'KEYCLOAK_AUTHENTICATION_EXEMPT_PATHS'):
            path = request.path_info.lstrip('/')

            if any(re.match(m, path) for m in
                   settings.KEYCLOAK_AUTHENTICATION_EXEMPT_PATHS):
                return

        logger.debug('Hier')
        if self.header not in request.META:
            return HttpResponseNotAuthorized(
                attributes={'realm': request.realm.name})
        logger.debug(request.META[self.header])
        try:
            oidc_profile = django_keycloak.services.oidc_profile\
                .get_or_create_from_id_token(
                    client=request.realm.client,
                    id_token=request.META[self.header].split(' ')[1]
                )
            request.user = oidc_profile.user
        except ExpiredSignatureError:
            # If the signature has expired.
            return HttpResponseNotAuthorized(
                attributes={
                    'realm': request.realm.name,
                    'error': 'invalid_token',
                    'error_description': 'The access token is expired'
                }
            )
        except JWTClaimsError:
            return HttpResponseNotAuthorized(
                status=403,
                attributes={
                    'scope': ''
                }
            )
        except JWTError:
            # The signature is invalid in any way.
            return HttpResponseNotAuthorized(
                attributes={
                    'realm': request.realm.name,
                    'error': 'invalid_token',
                    'error_description': 'The access token is malformed'
                }
            )


