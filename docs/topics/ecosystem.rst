=========
Ecosystem
=========

As explained in the main goals part of Zinnia, any feature that can be
provided by another reusable app has been left out. This principle must
be applied from downstream to upstream.

This principle has already been applied to the downstream part, by strictly
selecting the dependancies required by Zinnia, in order not to reinvent the
wheel and to respect the DRY principles.

Now it's time to talk about the upstream part. Zinnia is made to be
*Ready To Use* by providing all the core functionalities required by a
Weblog application.
But sometimes even a full Weblog is not enough, so Zinnia has also been
made fully extendable, so it encourages and facilitates the creation of
extensions.

Since Zinnia has become stable, documented and reviewed, some extensions
have been built to enhance the core functionalities of the Weblog. These
extensions act like an ecosystem: they add multiple layers of
functionnalities around the core - which is Django and Zinnia - and they
allow interaction between each layer independently.

Of course, your Zinnia's Weblog can run without theses extensions, but you
might find some that suit your needs.

.. note::
   If you have written or are aware of an extension that can enhance the
   Zinnia's ecosystem, please share your code or information by sending
   me a `message`_. Your extension will then be listed here.


cmsplugin-zinnia
================

Cmsplugin-zinnia is a bridge between `Django-CMS`_ and Zinnia.

This package provides plugins, menus and apphook for integrating your
Zinnia powered Weblog into your django-cms Website.

The code bundled in this application is a copy of the original
``zinnia.plugins`` module, made for forward compatibility with
django-blog-zinnia > 0.11.

URL: https://github.com/Fantomas42/cmsplugin-zinnia

admin-tools-zinnia
==================

Admin-tools-zinnia is an extension based on `django-admin-tools`_ providing
new dashboard modules for your admin interface, related to your Weblog.

Useful for having a sexier admin interface.

URL: https://github.com/Fantomas42/admin-tools-zinnia

zinnia-theme-html5
==================

Zinnia-theme-html5 is an extension theme for making your Zinnia's Weblog
HTML5 ready.

URL: https://github.com/Fantomas42/zinnia-theme-html5

zinnia-theme-bootstrap
======================

Zinnia-theme-bootstrap is an extension theme for your Weblog based on
`Bootstrap`_.

URL: https://github.com/Fantomas42/zinnia-theme-bootstrap

byteflow2zinnia
===============

Migrate your users, tags, command and posts from Byteflow to Zinnia by
Richard Espelin.

URL: https://bitbucket.org/resplin/byteflow2zinnia

.. _`message`: https://github.com/Fantomas42
.. _`Django-CMS`: http://www.django-cms.org/
.. _`django-admin-tools`: http://django-admin-tools.readthedocs.org/en/latest/index.html
.. _`Bootstrap`: http://twitter.github.com/bootstrap/
