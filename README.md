# Django Keycloak

[![Build Status](https://www.travis-ci.org/Peter-Slump/django-keycloak.svg?branch=master)](https://www.travis-ci.org/Peter-Slump/django-keycloak)

Django app to add Keycloak  support to your project.

[Read documentation](http://django-keycloak.readthedocs.io/en/latest/)

http://www.keycloak.org/

## Development

Install development environment:

```bash
$ make install-python
```

### Writing docs

Documentation is written using Sphinx and maintained in the docs folder.

To make it easy to write docs Docker support is available.

First build the Docker container:

    $ docker build . -f DockerfileDocs -t django-keycloak-docs

Run the container

    $ docker run -v `pwd`:/src --rm -t -i -p 8050:8050 django-keycloak-docs

Go in the browser to http://localhost:8050 and view the documentation which get
refreshed and updated on every update in the documentation source.