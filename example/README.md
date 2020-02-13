# Example project

This folder contains an example showcase project for the Django Keycloak project.

It consists out of three applications:
 - identity server (Keycloak)
 - resource provider (small web application)
 - resource provider (API accessible)
 
When running the application everything is pre-configured and ready to use.

Keycloak version 4.8.3-Final is used since that is the latest version which is 
commercially supported by Red Hat (SSO).

You can find the docs for this version here: https://www.keycloak.org/archive/documentation-4.8.html

You can find the following features in the project:

- Authentication (login)
- Authorisation (permissions)
- Token Exchange

## Run the project

Installation of Docker and Docker-compose is required

Run:

    $ docker-compose up
    
In your browser visit: https://resource-provider.localhost.yarf.nl/

Accept the insecure certificate, or add the CA which you can find in `nginx/certs/ca.pem` to your trusted CA's.

## Credentials

Keycloak admin user:

- username: admin
- password: password

"Test user" in example Realm

- username: testuser
- password: password

Django admin user (Resource Provider & Resource Provider API)

- username: admin
- password: password

## Import/Export

Using the `command` section in the keycloak configuration in the docker-compose file.
Docs: https://www.keycloak.org/docs/latest/server_admin/index.html#_export_import
