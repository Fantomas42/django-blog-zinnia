================
Upgrading Zinnia
================

.. highlightlang:: console

If you want to upgrade your installation of Zinnia from a previous release,
it's easy, but you need to be cautious. The whole process takes less than
15 minutes.

.. _dumping-datas:

Dumping
=======

The first thing to do is a to dump your data for safety reasons. ::

  $ python manage.py dumpdata --indent=2 zinnia > dump_zinnia_before_migration.json

.. _update-zinnia-code:

Update Zinnia's code
====================

We are now ready to upgrade Zinnia. If you want to use the latest stable
version use :program:`easy_install` with this command: ::

  $ easy_install -U django-blog-zinnia

or if you prefer to upgrade from the development release, use
:program:`pip` like that: ::

  $ pip install -U -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

.. _update-database:

Update the database
===================

The database should probably be updated to the latest database schema of
Zinnia. ::

  $ python manage.py migrate zinnia

The database is now up to date, and ready to use.

.. _check-list:

Check list
==========

In order to finish the upgrade process, we must check if everything works
fine by browsing the Web site.

By experience, problems mainly come from customized templates,
because of changes in the URL reverse functions.
