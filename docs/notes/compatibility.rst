=============
Compatibility
=============

Zinnia tries to fit a maximum to the Django's standards to gain in
readability and to be always present when the version 3.4.2 of Django will
be here. :)

Predicting the future is a good thing, because it's coming soon.
Actually Zinnia is designed to handle the 1.10.x version and will reach the
release 1.12 easily without major changes.

https://docs.djangoproject.com/en/dev/internals/deprecation/

But the evolution of Django causes some backward incompatible changes, so
for the developers who have to maintain a project with an old version of
Django, it can be difficult to find which version of Zinnia to choose.

.. _zinnia-django-compatibility:

Compatibility with Django
=========================

Here a list establishing the compatibility between Zinnia and Django:

.. versionchanged:: 0.20

Backward incompatibilities with Django v1.11.x due to :

* Removal of Python 2 code

.. versionchanged:: 0.19

Backward incompatibilities with Django v1.10.x due to :

* Removal of Select.render_option() method

.. versionchanged:: 0.18

Backward incompatibilities with Django v1.9.x due to :

* Removal of allow_tags property in django.contrib.admin
* Changes in prototype of widget.render_options
* Use of the new property user.is_authenticated

.. versionchanged:: 0.17

Backward incompatibilities with Django v1.8.x due to :

* Usage of Field.remote_field.
* Usage of the new template tag syntax.
* Changes around the application namespace.

.. versionchanged:: 0.16

Backward incompatibilities with Django v1.7.x due to :

* Usage of the new TEMPLATES API.
* Remove of templates tags loaded from future.

.. versionchanged:: 0.15

Backward incompatibilities with Django v1.6.x due to :

* Usage of the new migrations.
* Usage of the new lru_cache function.
* Usage of Admin.get_changeform_initial_data method.

.. versionchanged:: 0.14

Backward incompatibilities with Django v1.5.x due to :

* Usage of Queryset.datetimes().
* Handle savepoints in tests.

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
