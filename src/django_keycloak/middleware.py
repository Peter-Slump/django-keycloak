import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from django_keycloak.models import Realm
from django_keycloak.auth import get_remote_user
from django_keycloak.response import HttpResponseNotAuthorized


def get_realm(request):
    if not hasattr(request, '_cached_realm'):
        request._cached_realm = Realm.objects.first()
    return request._cached_realm


def get_user(request, origin_user):
    # Check for the user as set by
    # django.contrib.auth.middleware.AuthenticationMiddleware
    if not isinstance(origin_user, AnonymousUser):
        return origin_user

    if not hasattr(request, '_cached_user'):
        request._cached_user = get_remote_user(request)
    return request._cached_user


class BaseKeycloakMiddleware(MiddlewareMixin):

    set_session_state_cookie = True

    def process_request(self, request):
        """
        Adds Realm to request.
        :param request: django request
        """
        request.realm = SimpleLazyObject(lambda: get_realm(request))

    def process_response(self, request, response):

        if self.set_session_state_cookie:
            return self.set_session_state_cookie_(request, response)

        return response

    def set_session_state_cookie_(self, request, response):

        if not request.user.is_authenticated \
                or not hasattr(request.user, 'oidc_profile'):
            return response

        jwt = request.user.oidc_profile.jwt
        if not jwt:
            return response

        cookie_name = getattr(settings, 'KEYCLOAK_SESSION_STATE_COOKIE_NAME',
                              'session_state')

        # Set a browser readable cookie which expires when the refresh token
        # expires.
        response.set_cookie(
            cookie_name, value=jwt['session_state'],
            expires=request.user.oidc_profile.refresh_expires_before,
            httponly=False
        )

        return response


class KeycloakStatelessBearerAuthenticationMiddleware(BaseKeycloakMiddleware):

    set_session_state_cookie = False
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


class RemoteUserAuthenticationMiddleware(MiddlewareMixin):
    set_session_state_cookie = False

    def process_request(self, request):
        """
        Adds user to the request when authorized user is found in the session
        :param django.http.request.HttpRequest request: django request
        """
        origin_user = getattr(request, 'user', None)

        request.user = SimpleLazyObject(lambda: get_user(
            request,
            origin_user=origin_user
        ))
