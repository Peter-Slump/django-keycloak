# Django Keycloak

[![Build Status](https://www.travis-ci.org/Peter-Slump/django-keycloak.svg?branch=master)](https://www.travis-ci.org/Peter-Slump/django-keycloak)
[![Documentation Status](https://readthedocs.org/projects/django-keycloak/badge/?version=latest)](http://django-keycloak.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/Peter-Slump/django-keycloak/branch/master/graph/badge.svg)](https://codecov.io/gh/Peter-Slump/django-keycloak)
[![Maintainability](https://api.codeclimate.com/v1/badges/eb19f47dc03dec40cea7/maintainability)](https://codeclimate.com/github/Peter-Slump/django-keycloak/maintainability)

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