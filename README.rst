==================
Django Blog Zinnia
==================

Simple but powerfull application for managing a blogs into your Django website.

.. contents::

Features
========

More than a long speech, here the list of the main features :

  * Comments
  * RSS Feeds
  * Search engine
  * Archives views
  * Collaborative work
  * Widgets (Popular entries, Recent entries, ...)
  * Support Gravatar
  * Spam protection with Akismet
  * Prepublication

Dependancies
============

Before installing Zinnia make sure that you already have installed this packages

 * akismet
 * django-tagging

Installation
============

You could retrieve the last sources from http://github.com/Fantomas42/django-blog-zinnia and running the installation script ::
    
  $> python setup.py install

or use pip ::

  $> pip install -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

Applications
------------

Then register **zinnia**, **django.contrib.admin**, **django.contrib.comments** and **tagging** in the INSTALLED_APPS section of your project's settings. ::

  >>> INSTALLED_APPS = (
  ...   # Your favorites apps
  ...   'django.contrib.comments',
  ...   'django.contrib.admin',
  ...   'tagging',
  ...   'zinnia',)

Urls
----

In your project urls.py adding this following lines to include the zinnia's urls for serving the blog. ::

  >>> url(r'^weblog/', include('zinnia.urls')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),


Note the zinnia urlset is provided for convenient usage, but you can do something like that if you want to customize your urls : ::

  >>> url(r'^weblog/feeds/', include('zinnia.urls.feeds')),
  >>> url(r'^weblog/authors/', include('zinnia.urls.authors')),
  >>> url(r'^weblog/categories/', include('zinnia.urls.categories')),
  >>> url(r'^weblog/search/', include('zinnia.urls.search')),
  >>> url(r'^weblog/', include('zinnia.urls.entries')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),


Synchronization
---------------

Now you can run a *syncdb* for installing the models into your database.

