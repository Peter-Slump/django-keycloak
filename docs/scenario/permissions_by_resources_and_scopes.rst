===================================
Permissions by resources and scopes
===================================

Next to :ref:`permission_by_roles` you can also implement permissions by syncing
Django models as resources in Keycloak and the
`default permissions <https://docs.djangoproject.com/en/2.0/topics/auth/default/#default-permissions>`_
in Django as scopes in Keycloak.

Setup
=====

To configure Django Keycloak to make use of the Resource / Scope method of
permission assigning add the following setting:

.. code-block:: python

    # your-project/settings.py
    KEYCLOAK_PERMISSIONS_METHOD = 'resource'


Synchronization
===============

In Keycloak enable "Remote Resource Management" for the client:

.. image:: /keycloak_remote_resource_management.png

You can use the Django Admin action "Synchronize models as Keycloak resources"
to synchronize models and scopes to Keycloak.

.. image:: /synchronize_resources.png

An alternative is to run the Django management command `keycloak_sync_resources`:

.. code-block:: bash

    $ python manage.py keycloak_sync_resources

Optionally you can supply a client to which the resources should be synchronized.

Usage
=====

After synchronizing you can find the the models as resources and the default permissions as scopes:

Resources:

.. image:: /keycloak_resources.png

Scopes:

.. image:: /keycloak_scopes.png

From here you are able to configure your `policies` and `permissions` and assign
them to `users` of `groups` using `roles` in Keycloak. Once assigned you get
them back as permissions in Django where the policies are combined with the
resources just like you are used to in the default Django permission system
i.e. `foo.add_bar` or `foo.change_bar`.
