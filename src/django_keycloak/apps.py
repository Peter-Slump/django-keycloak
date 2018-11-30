from django.conf import settings
from django.apps.config import AppConfig


class KeycloakAppConfig(AppConfig):
    name = 'django_keycloak'
    verbose_name = 'Keycloak'

    def get_models(self, include_auto_created=False, include_swapped=False):
        self.apps.check_models_ready()
        for model in self.models.values():
            if not settings.AUTH_USER_MODEL:
                if model._meta.object_name is 'KeycloakOpenIDProfile':
                    continue
            else:
                if model._meta.object_name is 'KeycloakRemoteUserOpenIDProfile':
                    continue

            if model._meta.auto_created and not include_auto_created:
                continue
            if model._meta.swapped and not include_swapped:
                continue
            yield model


