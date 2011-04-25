URL Shortener
=============

The URL shortening has becoming a big deal of the Internet especially for
transfering long URLs.

And so many URL shortening services exist, each with his own features.

Originaly Zinnia provided a only way to generate short urls for your
entries, and you needed to install *django_bitly*.

One way it's not bad, but it's not enough.

First of all Zinnia now provides his own short URLs for the entries, ex :

  http://mydomain.com/blog/1/

Of course the URL is short (and can be shorter) but if you have a long
domain, the URL can be not so short, ex :

  http://mysuperverylongdomain.com/blog/1/ (40 characters !)

But now you can easily change this behavior and use your favorite URL
shortener service by writing a backend.


Writing your own URL shortener backend
--------------------------------------

Writing a backend for using your custom URL shortener is simple as
possible, you only needs to follows 4 rules.

 * In a new python file write a function named **backend** taking an Entry
   instance in parameters.

 * The **backend** function should returns an URL including the protocol
   and the domain.

 * If the **backend** requires initial configuration you must raise a
   *django.core.exceptions.ImproperlyConfigured* exception if the
   configuration is not valid. The error will be displayed in the console.

 * Register your backend to be used in your project with this setting : ::

   ZINNIA_URL_SHORTENER_BACKEND = 'path.to.your.url.shortener.module'


For a complete examples take a look in this folder : zinnia/url_shortener/backends/.
