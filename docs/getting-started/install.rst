============
Installation
============

.. module:: zinnia

.. _dependencies:

Dependencies
============

Make sure to install these packages prior to installation :

* `Python`_ >= 2.6.5
* `Django`_ >= 1.5
* `PIL`_ >= 1.1.6 or `Pillow`_ >= 2.0.0
* `django-mptt`_ >= 0.5.1 < 0.6
* `django-tagging`_ >= 0.3.1
* `beautifulsoup4`_ >= 4.1.3

The packages below are optionnal but needed for run the full test suite or
migrate the database.

* `pytz`_
* `South`_ >= 0.7.6
* `pyparsing`_ >= 1.5.5 < 2.0.0
* `django-xmlrpc`_ >= 0.1.5

Note that all the needed dependencies will be resolved if you install
Zinnia with :program:`pip` or :program:`easy_install`, excepting Django.

.. _getting-the-code:

Getting the code
================

.. highlight:: console

For the latest stable version of Zinnia use :program:`easy_install`: ::

  $ easy_install django-blog-zinnia

or use :program:`pip`: ::

  $ pip install django-blog-zinnia

You could also retrieve the last sources from
https://github.com/Fantomas42/django-blog-zinnia. Clone the repository
using :program:`git` and run the installation script: ::

  $ git clone git://github.com/Fantomas42/django-blog-zinnia.git
  $ cd django-blog-zinnia
  $ python setup.py install

or more easily via :program:`pip`: ::

  $ pip install -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

.. _applications:

Applications
============

.. highlight:: python

Assuming that you have an already existing Django project, register
:mod:`zinnia`, and these following applications in the
:setting:`INSTALLED_APPS` section of your project's settings. ::

  INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'tagging',
    'mptt',
    'zinnia',
  )

.. _template-context-processors:

Template Context Processors
===========================

Add these following
:setting:`template context processors<TEMPLATE_CONTEXT_PROCESSORS>` if not
already present. ::

  TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'zinnia.context_processors.version',) # Optional

.. _urls:

URLs
====

Add at least these following lines to your project's urls.py in order to
display the Weblog. ::

  url(r'^weblog/', include('zinnia.urls')),
  url(r'^comments/', include('django.contrib.comments.urls')),

Remember to enable the :mod:`~django.contrib.admin` site in the urls.py of
your project if you haven't done it yet for having the edition capabilities.

Note that the default Zinnia URLset :mod:`zinnia.urls` is calibrated for
convenient usage, but you can customize your Weblog URLs as you
want. Here's a custom implementation of the URLs provided by Zinnia: ::

  url(r'^', include('zinnia.urls.capabilities')),
  url(r'^search/', include('zinnia.urls.search')),
  url(r'^sitemap/', include('zinnia.urls.sitemap')),
  url(r'^trackback/', include('zinnia.urls.trackback')),
  url(r'^blog/tags/', include('zinnia.urls.tags')),
  url(r'^blog/feeds/', include('zinnia.urls.feeds')),
  url(r'^blog/random/', include('zinnia.urls.random')),
  url(r'^blog/authors/', include('zinnia.urls.authors')),
  url(r'^blog/categories/', include('zinnia.urls.categories')),
  url(r'^blog/comments/', include('zinnia.urls.comments')),
  url(r'^blog/', include('zinnia.urls.entries')),
  url(r'^blog/', include('zinnia.urls.archives')),
  url(r'^blog/', include('zinnia.urls.shortlink')),
  url(r'^blog/', include('zinnia.urls.quick_entry')),

.. _static-files:

Static Files
============

Since the version 1.3 of Django, Zinnia uses the
:mod:`~django.contrib.staticfiles` application to serve the static files
needed. Please refer to
https://docs.djangoproject.com/en/dev/howto/static-files/ for more
informations about serving static files.

.. _syncing-database:

Syncing the database
====================

.. highlight:: console

Now that you have everything set up, simply run the following in your
project directory to sync the models with the database. ::

  $ python manage.py syncdb

If you are using `South`_ to manage your database, you will have to do the
following. ::

  $ python manage.py syncdb --migrate

.. _`Python`: http://www.python.org/
.. _`Django`: https://www.djangoproject.com/
.. _`PIL`: http://www.pythonware.com/products/pil/
.. _`Pillow`: http://python-imaging.github.io/Pillow/
.. _`django-mptt`: https://github.com/django-mptt/django-mptt/
.. _`django-tagging`: https://code.google.com/p/django-tagging/
.. _`beautifulsoup4`: http://www.crummy.com/software/BeautifulSoup/
.. _`pytz`: http://pytz.sourceforge.net/
.. _`pyparsing`: http://pyparsing.wikispaces.com/
.. _`django-xmlrpc`: https://github.com/Fantomas42/django-xmlrpc
.. _`South`: http://south.aeracode.org/
