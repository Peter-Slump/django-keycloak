import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from jose.exceptions import (
    ExpiredSignatureError,
    JWTClaimsError,
    JWTError,
)

import django_keycloak.services.oidc_profile


logger = logging.getLogger(__name__)


class KeycloakAuthorizationBase(object):

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

        rpt_decoded = django_keycloak.services.oidc_profile\
            .get_entitlement(oidc_profile=user_obj.oidc_profile)

        logger.debug(rpt_decoded)

        return [
            role for role in rpt_decoded['resource_access'].get(
                user_obj.oidc_profile.realm.client.client_id,
                {'roles': []}
            )['roles']
        ]

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        return perm in self.get_all_permissions(user_obj, obj)


class KeycloakAuthorizationCodeBackend(KeycloakAuthorizationBase):

    def authenticate(self, request, code, redirect_uri):

        if not hasattr(request, 'realm'):
            raise ImproperlyConfigured(
                'Add BaseKeycloakMiddleware to middlewares')

        keycloak_openid_profile = django_keycloak.services\
            .oidc_profile.update_or_create_from_code(
                client=request.realm.client,
                code=code,
                redirect_uri=redirect_uri
            )

        return keycloak_openid_profile.user


class KeycloakIDTokenAuthorizationBackend(KeycloakAuthorizationBase):

    def authenticate(self, request, access_token):

        if not hasattr(request, 'realm'):
            raise ImproperlyConfigured(
                'Add BaseKeycloakMiddleware to middlewares')

        try:
            oidc_profile = django_keycloak.services.oidc_profile\
                .get_or_create_from_id_token(
                    client=request.realm.client,
                    id_token=access_token
                )
        except ExpiredSignatureError:
            # If the signature has expired.
            logger.debug('KeycloakBearerAuthorizationBackend: failed to '
                         'authenticate due to an expired access token.')
        except JWTClaimsError as e:
            logger.debug('KeycloakBearerAuthorizationBackend: failed to '
                         'authenticate due to failing claim checks: "%s"'
                         % str(e))
        except JWTError:
            # The signature is invalid in any way.
            logger.debug('eycloakBearerAuthorizationBackend: failed to '
                         'authenticate due to a malformed access token.')
        else:
            return oidc_profile.user

        return None
