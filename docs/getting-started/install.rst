============
Installation
============

.. module:: zinnia

.. _dependencies:

Dependencies
============

Make sure to install these packages prior to installation :

* `Python 2.x`_ >= 2.5
* `Django`_ >= 1.4
* `django-mptt`_ >= 0.5.1 < 0.6
* `django-tagging`_ >= 0.3.1
* `BeautifulSoup`_ >= 3.2.0

The packages below are optionnal but needed for run the full test suite.

* `pyparsing`_ >= 1.5.5
* `django-xmlrpc`_ >= 0.1.3

Note that all the dependencies will be resolved if you install
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

Then register :mod:`zinnia`, and these following applications in the
:setting:`INSTALLED_APPS` section of your project's settings. ::

  INSTALLED_APPS = (
    # Your favorite apps
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'tagging',
    'mptt',
    'zinnia',)

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

Add the following lines to your project's urls.py in order to display the
blog. ::

  url(r'^weblog/', include('zinnia.urls')),
  url(r'^comments/', include('django.contrib.comments.urls')),

Note that the default zinnia URLset is provided for convenient usage, but
you can customize your URLs if you want. Here's how: ::

  url(r'^', include('zinnia.urls.capabilities')),
  url(r'^search/', include('zinnia.urls.search')),
  url(r'^sitemap/', include('zinnia.urls.sitemap')),
  url(r'^trackback/', include('zinnia.urls.trackback')),
  url(r'^weblog/tags/', include('zinnia.urls.tags')),
  url(r'^weblog/feeds/', include('zinnia.urls.feeds')),
  url(r'^weblog/authors/', include('zinnia.urls.authors')),
  url(r'^weblog/categories/', include('zinnia.urls.categories')),
  url(r'^weblog/discussions/', include('zinnia.urls.discussions')),
  url(r'^weblog/', include('zinnia.urls.entries')),
  url(r'^weblog/', include('zinnia.urls.archives')),
  url(r'^weblog/', include('zinnia.urls.shortlink')),
  url(r'^weblog/', include('zinnia.urls.quick_entry')),
  url(r'^comments/', include('django.contrib.comments.urls')),

.. _static-files:

Static Files
============

Since the version 1.3 of Django, Zinnia uses the
:mod:`django.contrib.staticfiles` application to serve the static files
needed. Please refer to
https://docs.djangoproject.com/en/dev/howto/static-files/ for more
informations about serving static files.

.. _`Python 2.x`: http://www.python.org/
.. _`Django`: https://www.djangoproject.com/
.. _`django-mptt`: https://github.com/django-mptt/django-mptt/
.. _`django-tagging`: https://code.google.com/p/django-tagging/
.. _`BeautifulSoup`: http://www.crummy.com/software/BeautifulSoup/
.. _`pyparsing`: http://pyparsing.wikispaces.com/
.. _`django-xmlrpc`: https://github.com/Fantomas42/django-xmlrpc
