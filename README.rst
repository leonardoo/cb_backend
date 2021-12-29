cb_backend
==========

backend

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter
     :target: https://github.com/cookiecutter/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style

:License: MIT

conclusions
--------------

for this app, i take in consideration the following:

- this can be done in a microframework for had a better performance
- for performance reasons, i use a cache system and dont use serializer base in models in many cases its better had a function to convert and return the data,
- the app require a group for the applications can share sessions
- without knowing how will the apps handle the session, i create a json field to had something similar to jwt data for multiple apps can get same sessions
- because a event can have multiple validators, i use a json field that will contains json schema, so we can add new validators easily
- the app case can be a app to collect data from multiple website, as an app for analytics or something like sentry to collect errors


.. _ `django-ninja':https://django-ninja.rest-framework.com/`

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ mypy cb_backend

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ pytest

Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd cb_backend
    celery -A config.celery_app worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.

Sentry
^^^^^^

Sentry is an error logging aggregator service. You can sign up for a free account at  https://sentry.io/signup/?code=cookiecutter  or download and host it yourself.
The system is setup with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

Deployment
----------

The following details how to deploy this application.

Docker
^^^^^^

See detailed `cookiecutter-django Docker documentation`_.

.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html
