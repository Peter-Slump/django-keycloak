.. _local_user_setup:

============================
Setup for local user storage
============================

.. toctree::
   :maxdepth: 4

By local user storage a
`User object <https://docs.djangoproject.com/en/2.0/topics/auth/default/#user-objects>`_
get created for every logged in identity. This can be handy when you want to
link objects to this User object. If that's not the case please read the
scenario for setting up remote user.

Since **this is the default behaviour for Django Keycloak** you don't have to
configure any setting.

Important to point out the `KEYCLOAK_OIDC_PROFILE_MODEL` setting. This should
contain `django_keycloak.OpenIdConnectProfile` (which is the case by default).
The model to store the Open ID Connect profile is a swappable model. When
configured to this model a foreign key to the configured Django User model is
available.

.. code-block:: python

    # settings.py
    KEYCLOAK_OIDC_PROFILE_MODEL = 'django_keycloak.OpenIdConnectProfile'