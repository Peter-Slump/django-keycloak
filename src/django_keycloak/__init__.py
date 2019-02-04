from . import app_settings as defaults
from django.conf import settings


default_app_config = 'django_keycloak.apps.KeycloakAppConfig'

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))
