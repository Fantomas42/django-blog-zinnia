======================
Advanced Configuration
======================

.. _zinnia-sitemaps:

Sitemaps
========

.. module:: zinnia.sitemaps

One of the cool features of Django is the sitemap application, so if you
want to fill your Web site's sitemap with the entries of your blog, follow
these steps.

* Register :mod:`django.contrib.sitemaps` in the :setting:`INSTALLED_APPS` section.
* Edit your project's URLs and add this code: ::

   from zinnia.sitemaps import TagSitemap
   from zinnia.sitemaps import EntrySitemap
   from zinnia.sitemaps import CategorySitemap
   from zinnia.sitemaps import AuthorSitemap

   sitemaps = {'tags': TagSitemap,
               'blog': EntrySitemap,
               'authors': AuthorSitemap,
               'categories': CategorySitemap,}

   urlpatterns += patterns(
       'django.contrib.sitemaps.views',
       url(r'^sitemap.xml$', 'index',
           {'sitemaps': sitemaps}),
       url(r'^sitemap-(?P<section>.+)\.xml$', 'sitemap',
           {'sitemaps': sitemaps}),)

.. _zinnia-akismet:

Akismet Anti-Spam
=================

.. module:: zinnia.spam_checker.backends.automattic

If you want to benefit of the Akismet spam protection on your comments,
it's possible to do it by installing the `akismet`_ Python module, and add
this setting: ::

  ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia.spam_checker.backends.automattic',)

.. important:: You need an API key. If you don't have any, get one for free at
   	       http://akismet.com/signup/ then set it in your project's
	       settings like this:

::

  AKISMET_SECRET_API_KEY = 'your key'

.. _zinnia-typepad:

TypePad Anti-Spam
=================

.. module:: zinnia.spam_checker.backends.typepad

It's also possible to benefit of the `TypePad AntiSpam`_ service to fight
the spam. Like the Akismet protection you need to install the `akismet`_
Python module.

Then register the TypePad AntiSpam protection with this setting: ::

  ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia.spam_checker.backends.typepad',)

.. important:: You need an API key. If you don't have any, get one for free at
	       http://antispam.typepad.com/info/get-api-key.html then set
	       it in your project's settings like this:

::

  TYPEPAD_SECRET_API_KEY = 'your key'

.. _zinnia-mollom:

Mollom Anti-Spam
================

.. module:: zinnia.spam_checker.backends.mollom

Another approach to fight the spam is provided by `Mollom`_, Zinnia
implement a backend to use this spam filtering service. Before configuring
the service, you need to install the `PyMollom`_ Python library and then
register the Mollom spam checking protection with this setting: ::

  ZINNIA_SPAM_CHECKER_BACKENDS = ('zinnia.spam_checker.backends.mollom',)

.. important:: You need a private and public keys to use this service.
               Get a free account at http://mollom.com/pricing then set
	       your keys in your project's settings like this:

::

  MOLLOM_PUBLIC_KEY = 'your public key'
  MOLLOM_PRIVATE_KEY = 'your private key'

.. _zinnia-bitly:

Bit.ly
======

.. module:: zinnia.url_shortener.backends.bitly

You find http://bit.ly useful and want to use it for your blog entries ?

It's simple, install `django-bitly`_ in your project's settings and add
these settings: ::

  BITLY_LOGIN = 'your bit.ly login'
  BITLY_API_KEY = 'your bit.ly api key'
  ZINNIA_URL_SHORTENER_BACKEND = 'zinnia.url_shortener.backends.bitly'

Zinnia will do the rest.

.. _zinnia-twitter:

Twitter
=======

When you post a new entry on your blog you might want to tweet it as well.

In order to do that, you first need to activate the :ref:`zinnia-bitly` support like
described above.

Then install `tweepy`_ and add these settings. ::

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
entry's title and the shortened URL of your entry.

.. _zinnia-django-cms:

Django-CMS
==========

.. module:: zinnia.plugins

If you use `django-CMS 2.0`_, Zinnia can be integrated into your pages,
thanks to the plugin system.

Simply register :mod:`zinnia.plugins` in the :setting:`INSTALLED_APPS`
section of your project's settings.

It will provides :class:`custom plugins<cms.plugin_base.CMSPluginBase>` for
adding entries into your pages, an :class:`~cms.app_base.CMSApp` and
:class:`~cms.menu_bases.CMSAttachMenu` classes for easy integration.

If you want to use the plugin system of django-CMS in your entries, an
extended EntryModel with a :class:`~cms.models.fields.PlaceholderField` is
provided.

Just add this line in your project's settings to use it. ::

  ZINNIA_ENTRY_BASE_MODEL = 'zinnia.plugins.placeholder.EntryPlaceholder'

.. seealso::
   :doc:`/how-to/extending_entry_model` for more information about the extension
   of the entry model.

.. warning::
   .. versionchanged:: 0.10

   :mod:`zinnia.plugins` is deprecated and will be removed in the future
   releases of Zinnia. Please use `cmsplugin_zinnia`_ instead.

.. _zinnia-tinymce:

TinyMCE
=======

If you want to replace WYMEditor by TinyMCE install `django-tinymce`_ and
follow the `installation instructions`_.

TinyMCE can be customized by overriding the
:file:`admin/zinnia/entry/tinymce_textareas.js` template.

.. _zinnia-markup-languages:

Markup languages
================

If you doesn't want to write your entries in HTML, because you are
an über coder knowing more than 42 programming languages, you have the
possibility to use a custom markup language for editing the entries.

Currently **MarkDown**, **Textile** and **reStructuredText** are supported,
so if you want to use one of these languages, simply set this
variable as appropriate in your project's settings. ::

  ZINNIA_MARKUP_LANGUAGE = 'restructuredtext'

Note that the name of the language must be in lowercase.

More informations about the dependencies in :mod:`django.contrib.markup`.

.. _zinnia-xmlrpc:

XML-RPC
=======

.. module:: zinnia.xmlrpc

Zinnia provides few Webservices via XML-RPC, but before using it,
you need to install `django-xmlrpc`_.

Then register :mod:`django_xmlrpc` in your :setting:`INSTALLED_APPS`
section of your project's settings.

Now add these lines in your project's settings. ::

  from zinnia.xmlrpc import ZINNIA_XMLRPC_METHODS
  XMLRPC_METHODS = ZINNIA_XMLRPC_METHODS

:data:`ZINNIA_XMLRPC_METHODS` is a simple list of tuples containing all
the Webservices embedded in Zinnia.

If you only want to use the Pingback service import
:data:`ZINNIA_XMLRPC_PINGBACK`, or if you want you just want to enable the
`MetaWeblog API`_ import :data:`ZINNIA_XMLRPC_METAWEBLOG`.

You can also use your own mixins.

Finally we need to register the URL of the XML-RPC server.
Insert something like this in your project's urls.py: ::

  url(r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc'),

.. note:: For the Pingback service check if your site is enabled for
          pingback detection.
          More information at http://hixie.ch/specs/pingback/pingback-1.0#TOC2

.. _`akismet`: http://www.voidspace.org.uk/python/modules.shtml#akismet
.. _`TypePad AntiSpam`: http://antispam.typepad.com/
.. _`Mollom`: http://mollom.com/
.. _`PyMollom`: https://github.com/itkovian/PyMollom
.. _`django-bitly`: http://bitbucket.org/discovery/django-bitly/
.. _`tweepy`: https://github.com/tweepy/tweepy
.. _`cmsplugin_zinnia`: https://github.com/Fantomas42/cmsplugin-zinnia
.. _`django-CMS 2.0`: http://www.django-cms.org/
.. _`django-tinymce`: https://code.google.com/p/django-tinymce/
.. _`installation instructions`: http://django-tinymce.googlecode.com/svn/trunk/docs/.build/html/index.html
.. _`django-xmlrpc`: http://pypi.python.org/pypi/django-xmlrpc/
.. _`MetaWeblog API`: http://www.xmlrpc.com/metaWeblogApi
