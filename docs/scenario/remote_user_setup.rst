.. _remote_user_setup:

=====================
Setup for remote user
=====================

It's not required to create a local User object for every logged in identity.
If you don't need a local user object you can setup the app to work with a
remote user. This user behaves like Django's User object but it is not a real
one.

.. note:: For logging purposes Django admin only works with User objects which
    are stored in the database. So you cannot use this method to authenticate
    users for admin usage.

.. warning:: Set the configuration setting below before running the migrations!

Set the OIDC Profile model to the remote variant:

.. code-block:: python

    # your-project/settings.py
    KEYCLOAK_OIDC_PROFILE_MODEL = 'django_keycloak.RemoteUserOpenIdConnectProfile'

Configure the remote user middleware:

.. code-block:: python

    MIDDLEWARE = [
        ...

        'django_keycloak.middleware.BaseKeycloakMiddleware',
        'django_keycloak.middleware.RemoteUserAuthenticationMiddleware',
    ]

By default the class `django_keycloak.remote_user.KeycloakRemoteUser` is used as
user, this one will be available on the request when authenticated and will be
returned when you access `RemoteUserOpenIdConnectProfile.user`. If you want
another class (i.e. you need extra properties) you can configure this class
using the setting `KEYCLOAK_REMOTE_USER_MODEL`:

.. code-block:: python

    KEYCLOAK_REMOTE_USER_MODEL = 'django_keycloak.remote_user.KeycloakRemoteUser'