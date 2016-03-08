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

URL: https://github.com/django-blog-zinnia/cmsplugin-zinnia

admin-tools-zinnia
==================

Admin-tools-zinnia is an extension based on `django-admin-tools`_ providing
new dashboard modules for your admin interface, related to your Weblog.

Useful for having a sexier admin interface.

URL: https://github.com/django-blog-zinnia/admin-tools-zinnia

zinnia-threaded-comment
=======================

Zinnia-threaded-comments customizes the comment application bundled by
Django to enable replies to comments within your Weblog.

URL: https://github.com/django-blog-zinnia/zinnia-threaded-comments

zinnia-theme-html5
==================

Zinnia-theme-html5 is an extension theme for making your Zinnia's Weblog
HTML5 ready.

URL: https://github.com/django-blog-zinnia/zinnia-theme-html5

.. versionchanged:: 0.15.2
   This extension is no longer needed, because Zinnia is now HTML5 ready.

zinnia-theme-bootstrap
======================

Zinnia-theme-bootstrap is an extension theme for your Weblog based on
`Bootstrap`_.

URL: https://github.com/django-blog-zinnia/zinnia-theme-bootstrap

zinnia-theme-foundation
=======================

Zinnia-theme-foundation is an extension theme for your Weblog based on
`Zurb Foundation 5`_.

URL: https://github.com/django-blog-zinnia/zinnia-theme-foundation

zinnia-wysiwyg-wymeditor
========================

Zinnia-wysiwyg-wymeditor is an extension for editing your entries in the
admin with `WYMEditor`_.

URL: https://github.com/django-blog-zinnia/zinnia-wysiwyg-wymeditor

zinnia-wysiwyg-tinymce
======================

Zinnia-wysiwyg-tinymce is an extension for editing your entries in the
admin with `TinyMCE`_.

URL: https://github.com/django-blog-zinnia/zinnia-wysiwyg-tinymce

zinnia-wysiwyg-ckeditor
=======================

Zinnia-wysiwyg-ckeditor is an extension for editing your entries in the
admin with `CKeditor`_.

URL: https://github.com/django-blog-zinnia/zinnia-wysiwyg-ckeditor

zinnia-wysiwyg-markitup
=======================

Zinnia-wysiwyg-markitup is an extension for editing your entries in the
admin with `MarkItUp`_.

URL: https://github.com/django-blog-zinnia/zinnia-wysiwyg-markitup

zinnia-url-shortener-hashids
============================

Zinnia-url-shortener-bitly is an extension providing URL shortening for the
entries via `Hashids`_ algorithm.

URL: https://github.com/django-blog-zinnia/zinnia-url-shortener-hashids

zinnia-url-shortener-bitly
==========================

Zinnia-url-shortener-bitly is an extension providing URL shortening for the
entries via `Bit.ly`_.

URL: https://github.com/django-blog-zinnia/zinnia-url-shortener-bitly

zinnia-spam-checker-akismet
===========================

Zinnia-spam-checker-akismet is an extension adding anti-spam protection via
`Akismet`_ or Typepad.

URL: https://github.com/django-blog-zinnia/zinnia-spam-checker-akismet

zinnia-spam-checker-mollom
==========================

Zinnia-spam-checker-mollom is an extension adding anti-spam protection via
`Mollom`_.

URL: https://github.com/django-blog-zinnia/zinnia-spam-checker-mollom

zinnia-twitter
==============

Zinnia-twitter is an admin extension allowing you to post your entries on
`Twitter`_.

URL: https://github.com/django-blog-zinnia/zinnia-twitter

wordpress2zinnia
================

Migrate your Wordpress blog into Zinnia.

URL: https://github.com/django-blog-zinnia/wordpress2zinnia

blogger2zinnia
==============

Migrate your Blogger blog into Zinnia.

URL: https://github.com/django-blog-zinnia/blogger2zinnia

feed2zinnia
===========

Import RSS or Atom feeds into Zinnia.

URL: https://github.com/django-blog-zinnia/feed2zinnia

byteflow2zinnia
===============

Migrate your users, tags, command and posts from Byteflow to Zinnia by
Richard Espelin.

URL: https://bitbucket.org/resplin/byteflow2zinnia

zinnia-drupal
=============

Helper Django application for importing content from Drupal into Django
Blog Zinnia by Branko Majic.

URL: https://github.com/azaghal/zinnia-drupal

.. _`message`: https://github.com/Fantomas42
.. _`Django-CMS`: http://www.django-cms.org/
.. _`django-admin-tools`: http://django-admin-tools.readthedocs.org/en/latest/index.html
.. _`Bootstrap`: http://twitter.github.com/bootstrap/
.. _`Zurb Foundation 5`: http://foundation.zurb.com/
.. _`WYMEditor`: http://www.wymeditor.org/
.. _`TinyMCE`: http://www.tinymce.com/
.. _`CKEditor`: http://ckeditor.com/
.. _`MarkItUp`: http://markitup.jaysalvat.com/
.. _`Hashids`: http://hashids.org/
.. _`Bit.ly`: https://bitly.com/
.. _`Akismet`: http://akismet.com/
.. _`Mollom`: https://mollom.com/
.. _`Twitter`: https://twitter.com/
