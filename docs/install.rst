Installation
============

Dependencies
------------

Make sure to install these packages prior to installation :

 * Django
 * django-mptt
 * django-tagging
 * BeautifulSoup

The packages below are optionnal but needed for run the full test suite.

 * akismet
 * pyparsing
 * django-xmlrpc

Getting the code 
----------------

You could retrieve the last sources from
http://github.com/Fantomas42/django-blog-zinnia and run the installation
script ::

  $ python setup.py install

or use pip ::

  $ pip install -e git://github.com/Fantomas42/django-blog-zinnia.git#egg=django-blog-zinnia

For the latest stable version use easy_install ::

  $ easy_install django-blog-zinnia

Note that using *easy_install* or *pip* all the dependencies will be
resolved automaticaly.

Applications
------------

Then register **zinnia**, and these following applications in the
INSTALLED_APPS section of your project's settings. ::

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

Template Context Processors
---------------------------

Add these following template context processors if not already present. ::

  TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'zinnia.context_processors.version', # Optional
    'zinnia.context_processors.media',)

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

  url(r'^weblog/', include('zinnia.urls')),
  url(r'^comments/', include('django.contrib.comments.urls')),

Note that the default zinnia URLset is provided for convenient usage, but
you can customize your URLs if you want. Here's how : ::

  url(r'^', include('zinnia.urls.capabilities')),
  url(r'^search/', include('zinnia.urls.search')),
  url(r'^sitemap/', include('zinnia.urls.sitemap')),
  url(r'^trackback/', include('zinnia.urls.trackback')),
  url(r'^weblog/tags/', include('zinnia.urls.tags')),
  url(r'^weblog/feeds/', include('zinnia.urls.feeds')),
  url(r'^weblog/authors/', include('zinnia.urls.authors')),
  url(r'^weblog/categories/', include('zinnia.urls.categories')),
  url(r'^weblog/discussions/', include('zinnia.urls.discussions')),
  url(r'^weblog/', include('zinnia.urls.quick_entry')),
  url(r'^weblog/', include('zinnia.urls.entries')),
  url(r'^comments/', include('django.contrib.comments.urls')),
