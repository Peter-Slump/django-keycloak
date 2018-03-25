import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from django_keycloak.models import Realm
from django_keycloak.response import HttpResponseNotAuthorized


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


class KeycloakStatelessBearerAuthenticationMiddleware(BaseKeycloakMiddleware):

    header_key = "HTTP_AUTHORIZATION"

    def process_request(self, request):
        """
        Forces authentication on all requests except the URL's configured in
        the exempt setting.
        """
        super(KeycloakStatelessBearerAuthenticationMiddleware, self)\
            .process_request(request=request)

        if hasattr(settings, 'KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS'):
            path = request.path_info.lstrip('/')

            if any(re.match(m, path) for m in
                   settings.KEYCLOAK_BEARER_AUTHENTICATION_EXEMPT_PATHS):
                return

        if self.header_key not in request.META:
            return HttpResponseNotAuthorized(
                attributes={'realm': request.realm.name})

        user = authenticate(
            request=request,
            access_token=request.META[self.header_key].split(' ')[1]
        )

        if user is None:
            return HttpResponseNotAuthorized(
                attributes={'realm': request.realm.name})
        else:
            request.user = user
