======================================
Migrating from Django Auth to Keycloak
======================================

There are some tools available which can help by migrating a running project to
Keycloak.

--------
Add user
--------

A management command is available to create a Keycloak user based on a local
one.

.. code:: bash

    $ python manage.py keycloak_add_user --realm <insert realm name> --username <insert user name>

.. note:: In theory it would be possible to synchronize (hashed) passwords to
    Keycloak however Keycloak uses a 512 bit hash for pbkdf2_sha256 hashed
    passwords, Django generates a 256 bits hash. In that way passwords will not
    work when they are copied to Keycloak. The project includes a sha512 hasher
    (:class:`django_keycloak.hashers.PBKDF2SHA512PasswordHasher`) which you can
    configure to hash passwords in a Keycloak-complient way.

    .. code:: python

        # your-project/settings.py
        PASSWORD_HASHERS = [
            'django_keycloak.hashers.PBKDF2SHA512PasswordHasher',
        ]


.. _synchronize_permissions:

