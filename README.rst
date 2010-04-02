==================
Django Blog Zinnia
==================

Simple but powerfull application for managing a blogs into your Django website.

.. contents::

Features
========

More than a long speech, here the list of the main features :

  * Comments
  * Sitemaps
  * RSS Feeds
  * URL Shortener
  * Search engine
  * Archives views
  * Tags and categories views
  * Widgets (Popular entries, Recent entries, ...)
  * Spam protection with Akismet
  * Support Gravatar
  * Collaborative work
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

In your project's urls.py adding this following lines to include the zinnia's urls for serving the blog. ::

  >>> url(r'^weblog/', include('zinnia.urls')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),


Note the zinnia urlset is provided for convenient usage, but you can do something like that if you want to customize your urls : ::

  >>> url(r'^weblog/feeds/', include('zinnia.urls.feeds')),
  >>> url(r'^weblog/authors/', include('zinnia.urls.authors')),
  >>> url(r'^weblog/categories/', include('zinnia.urls.categories')),
  >>> url(r'^weblog/search/', include('zinnia.urls.search')),
  >>> url(r'^weblog/', include('zinnia.urls.entries')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),

Sitemap
-------

One of the cool features of Django is the sitemap application, 
so if you want to fill your website's sitemap with the entries of your blog, follow this procedure.

  * Register **django.contrib.sitemaps** in the INSTALLED_APPS section.
  * Edit your project's urls to add this code :

::

  >>> from zinnia.sitemaps import TagSitemap
  >>> from zinnia.sitemaps import EntrySitemap
  >>> from zinnia.sitemaps import CategorySitemap
  >>> from zinnia.sitemaps import AuthorSitemap
  >>> 
  >>> sitemaps = {'tags': TagSitemap,
  ...             'blog': EntrySitemap,
  ...             'authors': AuthorSitemap,
  ...             'categories': CategorySitemap,}
  ...
  >>> urlpatterns += patterns('django.contrib.sitemaps.views',
  ... 	                      (r'^sitemap.xml$', 'index',
  ...                          {'sitemaps': sitemaps}),
  ...                         (r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
  ...                          {'sitemaps': sitemaps}),
  ...			      )


Akismet
-------

By default the Akismet spam protection is enabled when someone leaving a comment.

But you need to have an API key, if you does not have, get a key at http://akismet.com/personal/ it's free.

Then set this intruction in your project's settings. ::

  >>> AKISMET_API_KEY = 'your key'

If you do not want spam protection for comments, you can disable it with this setting. ::

  >>> ZINNIA_AKISMET_COMMENT = False

Bit.ly
------

You find `Bit.ly
<http://bit.ly>`_ usefull and want to use it for your blog entries ?

It's simple, install `django_bitly
<http://bitbucket.org/discovery/django-bitly/>`_ in your project's settings and add these settings. ::

  >>> BITLY_LOGIN = 'Your Bit.ly login'
  >>> BITLY_API_KEY = 'Your Bit.ly api key'

Zinnia will do the rest.

Synchronization
---------------

Now you can run a *syncdb* for installing the models into your database.


Translations
============

If you want to contribute by updating a translation or adding a translation in your language,
it's simple, create a account on Transifex.net and you will have the possibility to edit the translations at this url :

http://www.transifex.net/projects/p/django-blog-zinnia/c/master/


Examples
========

  * `Fantomas' side
    <http://fantomas.willbreak.it>`_.

If you used Zinnia and liked it, don't hesitate to send me the url of your website, it will be added to the list.

