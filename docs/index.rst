===========================================
Welcome to Django Keycloak's documentation!
===========================================

.. toctree::
   :hidden:
   :caption: Scenario's
   :maxdepth: 2

   scenario/example_project
   scenario/local_user_setup
   scenario/remote_user_setup
   scenario/initial_setup
   scenario/migrating
   scenario/permissions_by_roles
   scenario/permissions_by_resources_and_scopes
   scenario/multi_tenancy

Django Keycloak adds Keycloak support to your Django project. It's build on top
of `Django's authentication system <https://docs.djangoproject.com/en/1.11/ref/contrib/auth/>`_.
It works side-by-side with the standard Django authentication implementation and
has tools to migrate your current users and permissions to Keycloak.

Features
========

- Multi tenancy support
- Permissions by roles or by resource/scope
- Choose if you want to create a local User model for every logged in identity or not.

Read :ref:`example_project` to quickly test this project.

.. note:: The documentation and the example project are all based on
    Keycloak version 3.4 since that is the latest version which is commercially
    supported by Red Hat (SSO).

Installation
============

Install requirement.

.. code-block:: bash

    $ pip install git+https://github.com/Peter-Slump/django-keycloak.git

Setup
=====

Some settings are always required and some other settings are dependant on how
you want to integrate Keycloak in your project.

Add `django-keycloak` to your installed apps, add the authentication back-end,
add the middleware, configure the urls and point to the correct login page.

.. code-block:: python

    # your-project/settings.py
    INSTALLED_APPS = [
        ....

        'django_keycloak.apps.KeycloakAppConfig'
    ]

    MIDDLEWARE = [
        ...

        'django_keycloak.middleware.BaseKeycloakMiddleware',
    ]

    AUTHENTICATION_BACKENDS = [
        ...

        'django_keycloak.auth.backends.KeycloakAuthorizationCodeBackend',
    ]

    LOGIN_URL = 'keycloak_login'

.. code-block:: python

    # your-project/urls.py
    ...

    urlpatterns = [
        ...

        re_path(r'^keycloak/', include('django_keycloak.urls')),
    ]


Before you actually start using Django Keycloak make an educated choice between
:ref:`local_user_setup` and :ref:`remote_user_setup`.

Then walk through the :ref:`initial_setup` to found out how to link your
Keycloak instance to your Django project.

If you don't want to take all that effort please read about :ref:`example_project`

Usage
=====

For requiring a logged in user you can just use the `standard Django
functionality <https://docs.djangoproject.com/en/1.11/topics/auth/default/#limiting-access-to-logged-in-users>`_.
This also counts for `enforcing permissions <https://docs.djangoproject.com/en/1.11/topics/auth/default/#the-permission-required-decorator>`_.

This app makes use of the `Python Keycloak client <https://github.com/Peter-Slump/python-keycloak-client>`_
