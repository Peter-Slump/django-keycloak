.. _example_project:

================================
Testing with the Example project
================================

The quickest way to experiment with this project is by running the example
project. This project is setup using Docker compose.

Given you have installed Docker and Docker compose run:

.. code-block:: bash

    $ cd example
    $ docker-compose up

The project exists of a resource provider which mimics a web app and a resource
provider which is only accessible by an API. Next to it is a Keycloak instance
available which is backed by a Postgres database.

Once you have the containers running you can access it by navigating to:
https://resource-provider.localhost.yarf.nl/ you can login with
username: `testuser` and password: `password`. The admin is
accessible at /admin with username: `admin` and password: `password`.

The Keycloak instance is available at:  https://identity.localhost.yarf.nl/
the username of the admin user is `admin` and the password is `password`.

The API is available at: https://resource-provider-api.localhost.yarf.nl/
You probably don't actually use this server or only for the admin. The admin is
accessible at /admin with username: `admin` and password: `password`.
