============
Installation
============

.. module:: zinnia

.. _dependencies:

Dependencies
============

Make sure to install these packages prior to installation :

* `Python`_ >= 3.5
* `Django`_ >= 2.2
* `Pillow`_ >= 7.0.0
* `django-mptt`_ >= 0.11.0
* `django-tagging`_ >= 0.5.0
* `beautifulsoup4`_ >= 4.8.2
* `mots-vides`_ >= 2015.5.11
* `pyparsing`_ >= 2.4.6
* `regex`_ >= 2020.2.20
* `django-contrib-comments`_ >= 1.9.2

The packages below are optionnal but needed for run the full test suite or
migrate the database.

* `django-xmlrpc`_ >= 0.1.8

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
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django_comments',
    'mptt',
    'tagging',
    'zinnia',
  )

.. _template-context-processors:

Template Context Processors
===========================

Add these following
:setting:`template context processors<TEMPLATE_CONTEXT_PROCESSORS>` if not
already present. ::

  TEMPLATES = [
    {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'APP_DIRS': True,
      'OPTIONS': {
        'context_processors': [
          'django.contrib.auth.context_processors.auth',
          'django.template.context_processors.i18n',
          'django.template.context_processors.request',
          'django.contrib.messages.context_processors.messages',
          'zinnia.context_processors.version',  # Optional
        ]
      }
    }
  ]

.. _urls:

URLs
====

Add at least these following lines to your project's urls.py in order to
display the Weblog. ::

  from django.conf.urls import include
  from django.conf.urls import url

  url(r'^weblog/', include('zinnia.urls')),
  url(r'^comments/', include('django_comments.urls')),

Remember to enable the :mod:`~django.contrib.admin` site in the urls.py of
your project if you haven't done it yet for having the edition capabilities.

Note that the default Zinnia URLset :mod:`zinnia.urls` is calibrated for
convenient usage, but you can customize your Weblog URLs as you
want. Here's a custom implementation of the URLs provided by Zinnia: ::

  blog_urls = ([
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
      url(r'^blog/', include('zinnia.urls.quick_entry'))
  ], 'zinnia')

  url(r'^', include(blog_urls))

.. _sites:

Sites
=====

Define the value of :setting:`SITE_ID` if not already done. ::

  SITE_ID = 1

.. _emails:

Emails
======

Be sure that the sending of emails is correctly configured, otherwise the
moderation system will not work. Please refer to
https://docs.djangoproject.com/en/dev/topics/email/ for more information
about sending emails.

.. _static-files:

Static Files
============

Since the version 1.3 of Django, Zinnia uses the
:mod:`~django.contrib.staticfiles` application to serve the static files
needed. Please refer to
https://docs.djangoproject.com/en/dev/howto/static-files/ for more
information about serving static files.

.. _syncing-database:

Syncing the database
====================

.. highlight:: console

Now that you have everything set up, simply run the following in your
project directory to sync the models with the database. ::

  $ python manage.py migrate

.. _`Python`: http://www.python.org/
.. _`Django`: https://www.djangoproject.com/
.. _`Pillow`: http://python-imaging.github.io/Pillow/
.. _`django-mptt`: https://github.com/django-mptt/django-mptt/
.. _`django-tagging`: https://code.google.com/p/django-tagging/
.. _`django-contrib-comments`: https://github.com/django/django-contrib-comments
.. _`mots-vides`: https://github.com/Fantomas42/mots-vides
.. _`regex`: https://pypi.python.org/pypi/regex
.. _`beautifulsoup4`: http://www.crummy.com/software/BeautifulSoup/
.. _`pytz`: http://pytz.sourceforge.net/
.. _`pyparsing`: http://pyparsing.wikispaces.com/
.. _`django-xmlrpc`: https://github.com/Fantomas42/django-xmlrpc
