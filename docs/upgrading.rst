Upgrading Zinnia
================

If you want to upgrade your installation of Zinnia from a previous release,
it's easy, but you need to be cautious. The whole process takes less than
15 minutes.

Dumping
-------

The first thing to do is a to dump your data for safety reasons. ::

  $ python manage.py dumpdata --indent=2 zinnia > dump_zinnia_before_migration.json

Preparing the database
----------------------

The main problem with the upgrade process is the database. The Zinnia's
models can have changed with new or missing fields.
That's why Zinnia use `South
<http://south.aeracode.org/>`_'s migrations to facilitate this step.

So we need to install the South package. ::

  $ easy_install south

South needs to be registered in your project's settings as an
INSTALLED_APPS. Once it is done, use syncdb to finish the
installtaion of South in your project. ::

  $ python manage.py syncdb

Now we will install the previous migrations of Zinnia to synchronize the
current database schema with South. ::

  $ python manage.py migrate zinnia --fake

Update Zinnia's code
--------------------

We are now ready to upgrade Zinnia. If you want to use the latest stable
version use easy_install with this command : ::

  $ easy_install -U zinnia

or if you prefer to upgrade from the development release, use pip like that : ::

  $ pip install -U -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

Update the database
-------------------

The database should probably be updated to the latest database schema of
Zinnia, South will be useful. ::

  $ python manage.py migrate zinnia

The database is now up to date, and ready to use.

Check list
----------

In order to finish the upgrade process, we must check if everything works
fine by browsing the website.

By experience, problems mainly come from customized templates,
because of changes in the url reverse functions.
