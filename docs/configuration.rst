Advanced Configuration
======================

Sitemaps
--------

One of the cool features of Django is the sitemap application, so if you
want to fill your website's sitemap with the entries of your blog, follow
these steps.

* Register **django.contrib.sitemaps** in the INSTALLED_APPS section.
* Edit your project's URLs and add this code :

::

   from zinnia.sitemaps import TagSitemap
   from zinnia.sitemaps import EntrySitemap
   from zinnia.sitemaps import CategorySitemap
   from zinnia.sitemaps import AuthorSitemap

   sitemaps = {'tags': TagSitemap,
               'blog': EntrySitemap,
               'authors': AuthorSitemap,
               'categories': CategorySitemap,}

   urlpatterns += patterns('django.contrib.sitemaps.views',
   	                   url(r'^sitemap.xml$', 'index',
                               {'sitemaps': sitemaps}),
                           url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
                               {'sitemaps': sitemaps}),)

Akismet
-------

If you want to benefit of the Akismet spam protection on your comments,
it's possible to do it by installing the `akismet`_ python module, and add
this setting: ::

  ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia.spam_checker.backends.automattic',)

.. important:: You need an API key. If you don't have any, get one for free at
   	       http://akismet.com/signup/ then set it in your project's
	       settings like this:

::

  AKISMET_SECRET_API_KEY = 'your key'

TypePad AntiSpam
----------------

It's also possible to benefit of the `TypePad AntiSpam
<http://antispam.typepad.com/>`_ service to fight the spam. Like the
Akismet protection you need to install the `akismet`_ python module.

The register the TypePad AntiSpam protection with this setting: ::

  ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia.spam_checker.backends.typepad',)

.. important:: You need an API key. If you don't have any, get one for free at
	       http://antispam.typepad.com/info/get-api-key.html then set
	       it in your project's settings like this:

::

  TYPEPAD_SECRET_API_KEY = 'your key'

Bit.ly
------

You find http://bit.ly useful and want to use it for your blog entries ?

It's simple, install `django_bitly
<http://bitbucket.org/discovery/django-bitly/>`_ in your project's settings
and add these settings: ::

  BITLY_LOGIN = 'your bit.ly login'
  BITLY_API_KEY = 'your bit.ly api key'
  ZINNIA_URL_SHORTENER_BACKEND = 'zinnia.url_shortener.backends.bitly'

Zinnia will do the rest.

Twitter
-------

When you post a new entry on your blog you might want to tweet it as well.

In order to do that, you first need to activate the Bit.ly support like
described above.

Then install `tweepy
<http://github.com/joshthecoder/tweepy>`_ and add these settings. ::

  TWITTER_CONSUMER_KEY = 'Your Consumer Key'
  TWITTER_CONSUMER_SECRET = 'Your Consumer Secret'
  TWITTER_ACCESS_KEY = 'Your Access Key'
  TWITTER_ACCESS_SECRET = 'Your Access Secret'

Note that the authentification for Twitter has changed since September 2010.
The actual authentification system is based on oAuth. That's why now you
need to set these 4 settings. If you don't know how to get these information,
follow this excellent tutorial at:

http://jmillerinc.com/2010/05/31/twitter-from-the-command-line-in-python-using-oauth/

Now in the admin, you can post an update containing your
entry's title and the shortened url of your entry.

Django-CMS
----------

If you use `Django-cms 2.0
<http://www.django-cms.org/>`_, Zinnia can be integrated into your pages,
thanks to the plugin system.

Simply register **zinnia.plugins** in the INSTALLED_APPS section of your
project's settings.

It will provides custom plugins for adding entries into your pages, an
App-Hook and Menus for easy integration.

If you want to use the plugin system of django-cms in your entries, an
extended EntryModel with a **PlaceholderField** is provided.

Add this line in your project's settings. ::

  ZINNIA_ENTRY_BASE_MODEL = 'zinnia.plugins.placeholder.EntryPlaceholder'

TinyMCE
-------

If you want to replace WYMEditor by TinyMCE install `django-tinymce
<http://code.google.com/p/django-tinymce/>`_ and follow the
`installation instructions
<http://django-tinymce.googlecode.com/svn/trunk/docs/.build/html/index.html>`_.

TinyMCE can be customized by overriding the
*admin/zinnia/entry/tinymce_textareas.js* template.

Markup languages
----------------

If you doesn't want to write your entries in HTML, because you are
an über coder knowing more than 42 programming languages, you have the
possibility to use a custom markup language for editing the entries.

Currently MarkDown, Textile and reStructuredText are supported,
so if you want to use one of these languages, simply set this
variable as appropriate in your project's settings. ::

  ZINNIA_MARKUP_LANGUAGE = 'restructuredtext'

Note that the name of the language must be in lowercase.

More informations about the dependencies at this URL :

http://docs.djangoproject.com/en/1.2/ref/contrib/markup/

XML-RPC
-------

Zinnia provides few webservices via XML-RPC, but before using it,
you need to install `django-xmlrpc
<http://pypi.python.org/pypi/django-xmlrpc/>`_.

Then register **django_xmlrpc** in your INSTALLED_APPS section of your
project's settings.

Now add these lines in your project's settings. ::

  from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
  XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

*ZINNIA_XMLRPC_METHODS* is a simple list of tuples containing all the
webservices embedded in Zinnia.

If you only want to use the Pingback service import
*ZINNIA_XMLRPC_PINGBACK*, or if you want you just want to enable the
`MetaWeblog API
<http://www.xmlrpc.com/metaWeblogApi>`_ import *ZINNIA_XMLRPC_METAWEBLOG*.

You can also use your own mixins.

Finally we need to register the url of the XML-RPC server.
Insert something like this in your project's urls.py: ::

  url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),

**Note** : For the Pingback service check if your site is enabled for
pingback detection.
More information at http://hixie.ch/specs/pingback/pingback-1.0#TOC2



.. `akismet`: http://www.voidspace.org.uk/python/modules.shtml#akismet
