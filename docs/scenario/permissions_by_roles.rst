.. _permission_by_roles:

====================
Permissions by roles
====================

There are two ways of using permissions one by roles and the other one by
resources/scopes. The roles method is the default one. In this method the
available client roles are available as permissions in your Django Project.

.. note:: Please read :ref:`synchronize_permissions` if you want to synchronize
    all available permissions in your current project to roles in Keycloak.

Setup
=====

Since this is the default method of handling permission you don't have to
configure anything. However it's good to know that the
`KEYCLOAK_PERMISSIONS_METHOD` is used to configure the way how permissions are
interpreted.

.. code-block:: python

    # your-project/settings.py
    KEYCLOAK_PERMISSIONS_METHOD = 'role'


Synchronize
===========

This Django Admin action which can be triggered for a realm synchronizes all
available permission to Keycloak. In keycloak the permissions will get
registered as roles. These roles can be added to a user.

For this feature the service account should have the
realm-management/manage-clients role assigned.

.. image:: /keycloak_manage_clients.png

This only makes sense when you use the `roles` permission method. You can read
about this at scenario: :ref:`permission_by_roles`.