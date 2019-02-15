import logging

from django_keycloak.app_settings import *  # noqa: F403,F401

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

LOGIN_URL = 'keycloak_login'
LOGOUT_REDIRECT_URL = 'index'

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'django_keycloak.apps.KeycloakAppConfig',
]

MIDDLEWARE = [
    'django_keycloak.middleware.BaseKeycloakMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend',
]

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}

logging.disable(logging.CRITICAL)
