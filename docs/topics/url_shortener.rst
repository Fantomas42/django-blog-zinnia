=============
URL Shortener
=============

.. module:: zinnia.url_shortener

.. versionadded:: 0.9

The URL shortening has becoming a big deal of the Internet especially for
transfering long URLs.

And so many URL shortening services exist, each with his own features.

Originally Zinnia provided a only way to generate short URLs for your
entries, and you needed to install mod:`django-bitly`.

One way it's not bad, but it's not enough.

Now Zinnia provides his own backend by default for making the URLs of the
entries shorter, example:

  http://mydomain.com/blog/2S/

This backend use the primary key of the entries, encoded in base 36 to
save a few more characters.

Of course the URL is short (and can be shorter) but if you have a long
domain, the URL can be not so short, example:

  http://mysuperverylongdomain.com/blog/15R/ (42 characters !)

But now you can easily change this behavior and use your favorite URL
shortener service by writing a backend shortening your URLs.

.. note:: The default backend is limited. When reaching the primary key
          **46656**, the short URLs generated enter in conflict with the
          archives by year.

          If you have reached this number of entries, it's effectively a
          good idea to change the default backend for a more scalable
          solution.

.. _writing-url-shortener:

Writing your own URL shortener backend
======================================

Writing a backend for using your custom URL shortener is simple as
possible, you only needs to follows 4 rules.

#. In a new Python file write a function named **backend** taking an
   :class:`~zinnia.models.entry.Entry` instance in parameters.

#. The **backend** function should returns an URL including the protocol
   and the domain.

#. If the **backend** requires initial configuration you must raise a
   :exc:`~django.core.exceptions.ImproperlyConfigured` exception if the
   configuration is not valid. The error will be displayed in the console.

#. Register your backend to be used in your project with this setting: ::

    ZINNIA_URL_SHORTENER_BACKEND = 'path.to.your.url.shortener.module'

Here the source code of the default backend. ::

    from django.contrib.sites.models import Site
    from django.core.urlresolvers import reverse
    from zinnia.settings import PROTOCOL

    def backend(entry):
        return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                              reverse('zinnia_entry_shortlink', args=[entry.pk]))

For a more examples take a look in this folder: :file:`zinnia/url_shortener/backends/`.
