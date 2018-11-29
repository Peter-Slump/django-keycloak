import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

import django_keycloak.services.keycloak_open_id_profile


logger = logging.getLogger(__name__)


class KeycloakAuthorizationCodeBackend(object):

    def get_user(self, user_id):
        # TODO: This is not going to work if we do not store the user, change this to create non-model-based object
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

        # TODO: This might need to change too, since it is not sure if the update_or_create can fill in .user
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

        # Todo: this will probably just work, but then we need to include the oidc_profile in the user

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
