=============
Compatibility
=============

Zinnia tries to fit a maximum to the Django's standards to gain in
readability and to be always present when the version 3.4.2 of Django will
be here. :)

Predicting the future is a good thing, because it's coming soon.
Actually Zinnia is designed to handle the 1.5.x version and will reach the
release 1.7 easily without major changes.

https://docs.djangoproject.com/en/dev/internals/deprecation/

But the evolution of Django causes some backward incompatible changes, so
for the developers who have to maintain a project with an old version of
Django, it can be difficult to find which version of Zinnia to choose.

.. _zinnia-django-compatibility:

Compatibility with Django
=========================

Here a list establishing the compatibility between Zinnia and Django:

.. versionchanged:: 0.13

Backward incompatibilities with Django v1.4.x due to :

* Experimental support of Python 3.
* Remove of the Python 2.5 support.
* Changes related to the archives views.
* Usage of the new syntax for the url templatetag.

.. versionchanged:: 0.11

Backward incompatibilities with Django v1.3.x due to :

* Time-zones support.
* Usage of the new features provided in the testrunner.

.. versionchanged:: 0.10

Backward incompatibilities with Django v1.2.x due to :

* Migration to the class-based generic views.
* Intensive usage of :mod:`django.contrib.staticfiles`.
* Usage of the new features provided in the testrunner.

.. versionchanged:: 0.6

Backward incompatibilities with Django v1.1.x due to :

* Migration of the feeds classes of :mod:`django.contrib.syndication`.

.. versionchanged:: 0.5

Backward incompatibilities with Django v1.0.x due to :

* Intensive usage of the actions in :mod:`django.contrib.admin`.
