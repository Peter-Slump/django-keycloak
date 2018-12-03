import logging

from django.contrib.auth import SESSION_KEY, HASH_SESSION_KEY, BACKEND_SESSION_KEY, get_user_model, _get_backends
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import rotate_token
from django.utils import timezone
from django.utils.crypto import constant_time_compare

import django_keycloak.services.keycloak_open_id_profile


logger = logging.getLogger(__name__)


class KeycloakAuthorizationCodeBackend(object):

    def get_user(self, user_id):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.select_related('oidc_profile__realm').get(
                pk=user_id)
        except UserModel.DoesNotExist:
            return None

        if user.oidc_profile.refresh_expires_before > timezone.now():
            return user

        return None

    def authenticate(self, request, code, redirect_uri):

        if not hasattr(request, 'realm'):
            raise ImproperlyConfigured(
                'Add BaseKeycloakMiddleware to middlewares')

        keycloak_openid_profile = django_keycloak.services\
            .keycloak_open_id_profile.update_or_create(
                realm=request.realm,
                code=code,
                redirect_uri=redirect_uri
            )

        return keycloak_openid_profile.user

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()
        if not hasattr(user_obj, '_keycloak_perm_cache'):
            user_obj._keycloak_perm_cache = self.get_keycloak_permissions(
                user_obj=user_obj)
        return user_obj._keycloak_perm_cache

    def get_keycloak_permissions(self, user_obj):
        if not hasattr(user_obj, 'oidc_profile'):
            return set()

        rpt_decoded = django_keycloak.services.keycloak_open_id_profile\
            .get_entitlement(oidc_profile=user_obj.oidc_profile)

        logger.debug(rpt_decoded)

        return [
            role for role in rpt_decoded['resource_access'].get(
                user_obj.oidc_profile.realm.client_id,
                {'roles': []}
            )['roles']
        ]

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)


class KeycloakRemoteUserAuthorizationCodeBackend(KeycloakAuthorizationCodeBackend):

    def get_user(self, user_id):
        return None

    def _get_user_session_key(self, request):
        """
        Overrides the default django.contrib.auth._get_user_session_key since it relies
        on a PK which is not supported for a non-database-backed user.
        :param request:
        :return:
        """
        return str(request.session[SESSION_KEY])

    def authenticate(self, request, code, redirect_uri):
        """

        :param request:
        :param code:
        :param redirect_uri:
        :return:
        """
        if not hasattr(request, 'realm'):
            raise ImproperlyConfigured(
                'Add BaseKeycloakMiddleware to middlewares')

        user = django_keycloak.services.keycloak_open_id_profile\
            .get_user_from_user_info(
                realm=request.realm,
                code=code,
                redirect_uri=redirect_uri
            )

        return user

    def login(self, request, user, backend=None):
        """
        Creates a session for the user.
        Based on the login function django.contrib.auth.login but uses a slightly different approach
        since the user is not backed by a database model.
        :param request:
        :param user:
        :param backend:
        :return:
        """
        session_auth_hash = ''
        if user is None:
            user = request.user
        if hasattr(user, 'get_session_auth_hash'):
            session_auth_hash = user.get_session_auth_hash()

        if SESSION_KEY in request.session:
            if self._get_user_session_key(request) != user.identifier or (
                    session_auth_hash and
                    not constant_time_compare(request.session.get(HASH_SESSION_KEY, ''), session_auth_hash)):
                # To avoid reusing another user's session, create a new, empty
                # session if the existing session corresponds to a different
                # authenticated user.
                request.session.flush()
        else:
            request.session.cycle_key()

        try:
            backend = backend or user.backend
        except AttributeError:
            backends = _get_backends(return_tuples=True)
            if len(backends) == 1:
                _, backend = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument or set the '
                    '`backend` attribute on the user.'
                )

        if not hasattr(user, 'identifier'):
            raise ValueError(
                'The user does not have an identifier or the identifier is empty.'
            )

        request.session[SESSION_KEY] = user.identifier
        request.session[BACKEND_SESSION_KEY] = backend
        request.session[HASH_SESSION_KEY] = session_auth_hash
        if hasattr(request, 'user'):
            request.user = user
        rotate_token(request)
        user_logged_in.send(sender=user.__class__, request=request, user=user)
