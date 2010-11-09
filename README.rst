==================
Django Blog Zinnia
==================

Simple yet powerful application for managing a blog within your Django website.

Zinnia has been made for publishing weblog entries and designed to do it well.

Basically any feature that can be provided by another reusable app has been
left out.
Why should we re-implement something that is already done and reviewed by
others and tested.

.. contents::

Features
========

Main features :

  * Comments
  * Sitemaps
  * Archives views
  * Related entries
  * Private entries
  * RSS or Atom Feeds
  * Tags and categories views
  * Advanced search engine
  * Prepublication and expiration
  * Widgets (Popular entries, Similar entries, ...)
  * Spam protection with Akismet
  * MetaWeblog API
  * Ping Directories
  * Ping External links
  * Bit.ly support
  * Twitter support
  * Gravatar support
  * Django-CMS plugins
  * Collaborative work
  * Tags autocompletion
  * Entry model extendable
  * Pingback/Trackback support
  * WYMeditor or TinyMCE support
  * WordPress conversion utility
  * Ready to use and extendables templates
  * Windows Live Writer compatibility

Take a look at the online demo at : http://django-blog-zinnia.com

Dependencies
============

Make sure to install these packages prior to installation :

 * akismet
 * django-mptt (0.4.1)
 * django-tagging
 * BeautifulSoup

The packages below are optionnal but needed for run the full test suite.

 * pyparsing
 * django-xmlrpc

Installation
============

You could retrieve the last sources from
http://github.com/Fantomas42/django-blog-zinnia and run the installation
script ::

  $> python setup.py install

or use pip ::

  $> pip install -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

For the latest stable version use easy_install ::

  $> easy_install django-blog-zinnia

Applications
------------

Then register **zinnia**, and these following applications in the
INSTALLED_APPS section of your project's settings. ::

  >>> INSTALLED_APPS = (
  ...   # Your favorite apps
  ...   'django.contrib.contenttypes',
  ...   'django.contrib.comments',
  ...   'django.contrib.sessions',
  ...   'django.contrib.sites',
  ...   'django.contrib.admin',
  ...   'tagging',
  ...   'mptt',
  ...   'zinnia',)

Template Context Processors
---------------------------

Add these following template context processors if not already present. ::

  >>> TEMPLATE_CONTEXT_PROCESSORS = (
  ...      'django.core.context_processors.auth',
  ...      'django.core.context_processors.i18n',
  ...      'django.core.context_processors.request',
  ...      'django.core.context_processors.media',
  ...      'zinnia.context_processors.media',
  ...      'zinnia.context_processors.version', # Optional
  ...	)

Media Files
-----------

You have to make a symbolic link from zinnia/media/zinnia directory to your
media directory or make a copy named **zinnia**, but if want to change this
value, define ZINNIA_MEDIA_URL in the settings.py as appropriate.

And don't forget to serve this URL.

URLs
----

Add the following lines to your project's urls.py in order to display the
blog. ::

  >>> url(r'^weblog/', include('zinnia.urls')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),


Note that the default zinnia URLset is provided for convenient usage, but
you can customize your URLs if you want. Here's how : ::

  >>> url(r'^', include('zinnia.urls.capabilities')),
  >>> url(r'^search/', include('zinnia.urls.search')),
  >>> url(r'^sitemap/', include('zinnia.urls.sitemap')),
  >>> url(r'^trackback/', include('zinnia.urls.trackback')),
  >>> url(r'^weblog/tags/', include('zinnia.urls.tags')),
  >>> url(r'^weblog/feeds/', include('zinnia.urls.feeds')),
  >>> url(r'^weblog/authors/', include('zinnia.urls.authors')),
  >>> url(r'^weblog/categories/', include('zinnia.urls.categories')),
  >>> url(r'^weblog/discussions/', include('zinnia.urls.discussions')),
  >>> url(r'^weblog/', include('zinnia.urls.entries')),
  >>> url(r'^comments/', include('django.contrib.comments.urls')),

Advanced Configuration
======================

Sitemap
-------

One of the cool features of Django is the sitemap application, so if you
want to fill your website's sitemap with the entries of your blog, follow
these steps.

  * Register **django.contrib.sitemaps** in the INSTALLED_APPS section.
  * Edit your project's URLs and add this code :

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

By default the Akismet spam protection is enabled when anyone leaves a
comment.

IMPORTANT : you need an API key. If you don't have any, get one for free at
http://akismet.com/personal/ then set it in your project's settings like
this : ::

  >>> AKISMET_SECRET_API_KEY = 'your key'

If you don't want spam protection for comments, you can disable it with
this setting. ::

  >>> ZINNIA_AKISMET_COMMENT = False

Bit.ly
------

You find `Bit.ly
<http://bit.ly>`_ useful and want to use it for your blog entries ?

It's simple, install `django_bitly
<http://bitbucket.org/discovery/django-bitly/>`_ in your project's settings
and add these settings. ::

  >>> BITLY_LOGIN = 'your bit.ly login'
  >>> BITLY_API_KEY = 'your bit.ly api key'

Zinnia will do the rest.

Twitter
-------

When you post a new entry on your blog you might want to tweet it as well.

In order to do that, you first need to activate the Bit.ly support like
described above.

Then install `tweepy
<http://github.com/joshthecoder/tweepy>`_ and add these settings. ::

  >>> TWITTER_CONSUMER_KEY = 'Your Consumer Key'
  >>> TWITTER_CONSUMER_SECRET = 'Your Consumer Secret'
  >>> TWITTER_ACCESS_KEY = 'Your Access Key'
  >>> TWITTER_ACCESS_SECRET = 'Your Access Secret'

Note that the authentification for Twitter has changed since September 2010.
The actual authentification system is based on oAuth. That's why now you
need to set these 4 settings. If you don't know how to get these information,
follow this excellent tutorial at:

http://jmillerinc.com/2010/05/31/twitter-from-the-command-line-in-python-using-oauth/

Now in the admin, you can post an update containing your
entry's title and the shortened url of your entry.

Django-CMS
----------

If you use `django-cms
<http://www.django-cms.org/>`_, Zinnia can be integrated into your pages,
thanks to the plugin system.

Simply register **zinnia.plugins** in the INSTALLED_APPS section of your
project's settings.

It will provides custom plugins for adding entries into your pages, an
App-Hook and Menus for easy integration.

If you want to use the plugin system of django-cms in your entries, an
extended EntryModel with a **PlaceholderField** is provided.

Add this line in your project's settings. ::

  >>> ZINNIA_ENTRY_BASE_MODEL = 'zinnia.plugins.placeholder.EntryPlaceholder'

TinyMCE
-------

If you want to replace WYMEditor by TinyMCE install `django-tinymce
<http://code.google.com/p/django-tinymce/>`_ and follow the
`installation instructions
<http://django-tinymce.googlecode.com/svn/trunk/docs/.build/html/index.html>`_.

TinyMCE can be customized by overriding the
*admin/zinnia/entry/tinymce_textareas.js* template.

XML-RPC
-------

Zinnia provides few webservices via XML-RPC, but before using it,
you need to install `django-xmlrpc
<http://pypi.python.org/pypi/django-xmlrpc/>`_.

Then register **django_xmlrpc** in your INSTALLED_APPS section of your
project's settings.

Now add these lines in your project's settings. ::

  >>> from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
  >>> XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

*ZINNIA_XMLRPC_METHODS* is a simple list of tuples containing all the
webservices embedded in Zinnia.

If you only want to use the Pingback service import
*ZINNIA_XMLRPC_PINGBACK*, or if you want you just want to enable the
`MetaWeblog API
<http://www.xmlrpc.com/metaWeblogApi>`_ import *ZINNIA_XMLRPC_METAWEBLOG*.

You can also use your own mixins.

Finally we need to register the url of the XML-RPC server.
Insert something like this in your project's urls.py: ::

  >>> url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),

**Note** : For the Pingback service check if your site is enabled for
pingback detection.
More information at http://hixie.ch/specs/pingback/pingback-1.0#TOC2

Template Tags
=============

Zinnia provides several template tags based on *inclusion_tag* system to
create some **widgets** in your website's templates.

* get_recent_entries(number=5, template="zinnia/tags/recent_entries.html")

Display the latest entries.

* get_random_entries(number=5, template="zinnia/tags/random_entries.html")

Display random entries.

* get_popular_entries(number=5, template="zinnia/tags/popular_entries.html")

Display popular entries.

* get_similar_entries(number=5, template="zinnia/tags/similar_entries.html")

Display entries similar to an existing entry.

* get_calendar_entries(year=auto, month=auto, template="zinnia/tags/calendar.html")

Display an HTML calendar with date of publications.

* get_archives_entries(template="zinnia/tags/archives_entries.html")

Display the archives by month.

* get_archives_entries_tree(template="zinnia/tags/archives_entries_tree.html")

Display all the archives as a tree.

* get_categories(template="zinnia/tags/categories.html")

Display all the categories available.

* get_recent_comments(number=5, template="zinnia/tags/recent_comments.html")

Display the latest comments.

* zinnia_breadcrumbs(separator="/", root_name="Blog", template="zinnia/tags/breadcrumbs.html")

Display the breadcrumbs for the pages handled by Zinnia.

* get_gravatar(email, size=80, rating='g', default=None)

Display the Gravatar image associated to an email, useful for comments.

Development
===========

A `Buildout
<http://pypi.python.org/pypi/zc.buildout>`_ script is provided to properly
initialize the project for anybody who wants to contribute to the project.

First of all, please use `VirtualEnv
<http://pypi.python.org/pypi/virtualenv>`_ to protect your system.

Follow these steps to start the development : ::

  $> git clone git://github.com/Fantomas42/django-blog-zinnia.git
  $> virtualenv --no-site-packages django-blog-zinnia
  $> cd django-blog-zinnia
  $> source ./bin/activate
  $> python bootstrap.py
  $> ./bin/buildout

The buildout script will resolve all the dependencies needed to develop the
application.

Once these operations are done, you are ready to develop the zinnia project.

Run this command to launch the tests. ::

  $> ./bin/test

To view the code coverage run this command. ::

  $> ./bin/cover

Execute these commands to check the code conventions. ::

  $> ./bin/pyflakes zinnia
  $> ./bin/pep8 --count -r --exclude=tests.py,migrations zinnia

To launch the demo site, execute these commands. ::

  $> ./bin/demo syncdb
  $> ./bin/demo loaddata helloworld
  $> ./bin/demo runserver

And for building the HTML documentation run this. ::

  $> ./bin/docs

Pretty easy no ?

Translations
============

If you want to contribute by updating a translation or adding a translation
in your language, it's simple: create a account on Transifex.net and you
can edit the translations at this URL :

http://www.transifex.net/projects/p/django-blog-zinnia/c/master/

Resources
=========

  * Online `documentation of Zinnia
    <http://django-blog-zinnia.com/docs/>`_.
  * Online `API of Zinnia module
    <http://django-blog-zinnia.com/docs/api/>`_.
  * Discussions and help at `Google Group
    <http://groups.google.com/group/django-blog-zinnia/>`_.
  * For reporting a bug or submitting a suggestion use `Github Issues
    <http://github.com/Fantomas42/django-blog-zinnia/issues/>`_.

Examples
========

  * `Demo site of Zinnia
    <http://django-blog-zinnia.com/blog/>`_.
  * `Fantomas' side
    <http://fantomas.willbreak.it>`_.
  * `Professional Web Studio
    <http://www.professionalwebstudio.com/en/weblog/>`_.
  * `mixedCase
    <http://www.mixedcase.nl/articles/>`_.


If you are a proud user of Zinnia, send me the URL of your website and I
will add it to the list.
