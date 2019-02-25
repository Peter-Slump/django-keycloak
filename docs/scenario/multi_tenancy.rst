=============
Multi-tenancy
=============

Django Keycloak supports multi tenancy by supporting multiple realms. The way to
determine the currently active realm is set to the request in the middleware.
In the project there is currently one middleware available. This is
`django_keycloak.middleware.BaseKeycloakMiddleware`. This middleware add the
first found Realm model to the request object.

.. code-block:: python

    # your-project/settings.py
    MIDDLEWARE = [
        ...

        'django_keycloak.middleware.BaseKeycloakMiddleware',
    ]

If you want to support multiple reams you have to create your own middleware.
There are several methods to determine the currently active realm. You can think
of realm determination by:

- Hostname
- Environment variable
- Selection during login
- etc.

It's up to you how the realm get determined and therefore it's also up to
you to `write a proper middleware <https://docs.djangoproject.com/en/2.0/topics/http/middleware/#writing-your-own-middleware>`_
for it. The only think the middleware has to make the correct Realm model to the
request as `request.realm`. This middleware has to be configured above other
middlewares which have to be configured for authentication purposes.