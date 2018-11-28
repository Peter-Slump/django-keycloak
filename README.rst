===============
Django Keycloak
===============

.. image:: https://www.travis-ci.org/Peter-Slump/django-keycloak.svg?branch=master
   :target: https://www.travis-ci.org/Peter-Slump/django-keycloak
   :alt: Build Status
.. image:: https://readthedocs.org/projects/django-keycloak/badge/?version=latest
   :target: http://django-keycloak.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://codecov.io/gh/Peter-Slump/django-keycloak/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Peter-Slump/django-keycloak
   :alt: codecov
.. image:: https://api.codeclimate.com/v1/badges/eb19f47dc03dec40cea7/maintainability
   :target: https://codeclimate.com/github/Peter-Slump/django-keycloak/maintainability
   :alt: Maintainability

Django app to add Keycloak  support to your project.

`Read documentation <http://django-keycloak.readthedocs.io/en/latest/>`_

http://www.keycloak.org/

Development
===========

Install development environment:

.. code:: bash

  $ make install-python

------------
Writing docs
------------

Documentation is written using Sphinx and maintained in the docs folder.

To make it easy to write docs Docker support is available.

First build the Docker container:

.. code:: bash

    $ docker build . -f DockerfileDocs -t django-keycloak-docs

Run the container

.. code:: bash

    $ docker run -v `pwd`:/src --rm -t -i -p 8050:8050 django-keycloak-docs

Go in the browser to http://localhost:8050 and view the documentation which get
refreshed and updated on every update in the documentation source.

--------------
Create release
--------------

.. code:: bash

    $ git checkout master
    $ git pull
    $ bumpversion release
    $ make deploy-pypi
    $ bumpversion --no-tag patch
    $ git push origin master --tags

Release Notes
=============

**unreleased**
**v0.1.1**