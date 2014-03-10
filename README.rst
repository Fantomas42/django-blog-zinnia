===============================================
Django Blog Zinnia |latest-version| |downloads|
===============================================

|travis-develop| |coverage-develop|

Simple yet powerful and really extendable application for managing a blog
within your Django Web site.

Zinnia has been made for publishing Weblog entries and designed to do it well.

Basically any feature that can be provided by another reusable app has been
left out.
Why should we re-implement something that is already done and reviewed by
others and tested?

|paypal|

Features
========

More than a long speech, here the list of the main features:

* Comments
* `Sitemaps`_
* Archives views
* Related entries
* Private entries
* RSS or Atom Feeds
* Tags and categories views
* `Advanced search engine`_
* Prepublication and expiration
* `Custom templates for various contents`_
* Editing in `Markdown`_, `Textile`_ or `reStructuredText`_
* Widgets (Popular entries, Similar entries, ...)
* Spam protection with `Akismet`_, `TypePad`_ or `Mollom`_
* Admin dashboard
* `MetaWeblog API`_
* Ping Directories
* Ping External links
* `Bit.ly`_ support
* `Twitter`_ support
* `Gravatar`_ support
* `Django-CMS`_ plugins
* Collaborative work
* Tags autocompletion
* `Entry model extendable`_
* Pingback/Trackback support
* `Blogger conversion utility`_
* `WordPress conversion utility`_
* `WYMeditor`_, `TinyMCE`_ and `MarkItUp`_ support
* Efficient database queries
* Ready to use and extendable templates
* `Compass`_ and `Sass3`_ integration
* `Windows Live Writer`_ compatibility

Examples
========

Take a look at the online demo at: http://demo.django-blog-zinnia.com/
or you can visit these websites who use Zinnia.

* `Fantomas' side`_  / `Mobile version`_
* `Darwin's Weblog`_
* `ShiningPanda`_
* `Tryolabs`_
* `AR.Drone Best of User Videos`_
* `Professional Web Studio`_
* `brainbreach`_
* `Mauro Bianchi`_
* `Sergey Miracle`_
* `Infantium`_
* `Pana`_
* `MAGIC Center at RIT`_
* `Rudolf Steiner School of Kreuzlingen`_
* `Vidzor Studio LLC`_

If you are a proud user of Zinnia, send me the URL of your website and I
will add it to the list.

Online resources
================

More information and help available at these URLs:

* `Code repository`_
* `Documentation`_
* `Travis CI server`_
* `Coverage report`_
* Discussions and help at `Google Group`_
* For reporting a bug use `GitHub Issues`_

.. |travis-develop| image:: https://travis-ci.org/Fantomas42/django-blog-zinnia.png?branch=develop
   :alt: Build Status - develop branch
   :target: http://travis-ci.org/Fantomas42/django-blog-zinnia
.. |coverage-develop| image:: https://coveralls.io/repos/Fantomas42/django-blog-zinnia/badge.png?branch=develop
   :alt: Coverage of the code
   :target: https://coveralls.io/r/Fantomas42/django-blog-zinnia
.. |latest-version| image:: https://pypip.in/v/django-blog-zinnia/badge.png
   :alt: Latest version on Pypi
   :target: https://crate.io/packages/django-blog-zinnia/
.. |downloads| image:: https://pypip.in/d/django-blog-zinnia/badge.png
   :alt: Downloads from Pypi
   :target: https://crate.io/packages/django-blog-zinnia/
.. |paypal| image:: https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif
   :alt:  Make a free donation with Paypal to encourage the development
   :target: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=68T48HR8KK9KG
.. _`Sitemaps`: http://docs.django-blog-zinnia.com/en/latest/getting-started/configuration.html#module-zinnia.sitemaps
.. _`Advanced search engine`: http://docs.django-blog-zinnia.com/en/latest/topics/search_engines.html
.. _`Custom templates for various contents`: http://docs.django-blog-zinnia.com/en/latest/getting-started/configuration.html#templates-for-entries
.. _`Markdown`: http://daringfireball.net/projects/markdown/
.. _`Textile`: http://redcloth.org/hobix.com/textile/
.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`Akismet`: http://akismet.com
.. _`TypePad`: http://antispam.typepad.com/
.. _`Mollom`: http://mollom.com/
.. _`MetaWeblog API`: http://www.xmlrpc.com/metaWeblogApi
.. _`Bit.ly`: http://docs.django-blog-zinnia.com/en/latest/getting-started/configuration.html#module-zinnia.url_shortener.backends.bitly
.. _`Twitter`: http://docs.django-blog-zinnia.com/en/latest/getting-started/configuration.html#twitter
.. _`Gravatar`: http://gravatar.com/
.. _`Django-CMS`: http://docs.django-blog-zinnia.com/en/latest/getting-started/configuration.html#django-cms
.. _`Entry model extendable`: http://django-blog-zinnia.rtfd.org/extending-entry
.. _`WYMeditor`: http://www.wymeditor.org/
.. _`TinyMCE`: http://tinymce.moxiecode.com/
.. _`MarkItUp`: http://markitup.jaysalvat.com/
.. _`Blogger conversion utility`: http://docs.django-blog-zinnia.com/en/latest/how-to/import_export.html#from-blogger-to-zinnia
.. _`WordPress conversion utility`: http://docs.django-blog-zinnia.com/en/latest/how-to/import_export.html#from-wordpress-to-zinnia
.. _`Compass`: http://compass-style.org/
.. _`Sass3`: http://sass-lang.com/
.. _`Windows Live Writer`: http://explore.live.com/windows-live-writer
.. _`Fantomas' side`: http://fantomas.willbreak.it/blog/
.. _`Mobile version`: http://m.fantomas.willbreak.it/blog/
.. _`Professional Web Studio`: http://www.professionalwebstudio.com/en/weblog/
.. _`Tryolabs`: http://www.tryolabs.com/Blog/
.. _`brainbreach`: http://brainbreach.com/
.. _`Mauro Bianchi`: http://www.maurobianchi.it/
.. _`Sergey Miracle`: http://sergeymiracle.com/weblog/
.. _`Infantium`: http://www.infantium.com/blog/
.. _`AR.Drone Best of User Videos`: http://ardrone.parrot.com/best-of-user-videos/
.. _`Darwin's Weblog`: http://darwin.willbreak.it/
.. _`ShiningPanda`: http://www.shiningpanda.com/blog/
.. _`Pana`: http://chusen87.com/news/
.. _`MAGIC Center at RIT`: http://magic.rit.edu/
.. _`Rudolf Steiner School of Kreuzlingen`: http://www.steinerschulekreuzlingen.ch/
.. _`Code repository`: https://github.com/Fantomas42/django-blog-zinnia
.. _`Documentation`: http://docs.django-blog-zinnia.com/
.. _`Travis CI server`: http://travis-ci.org/Fantomas42/django-blog-zinnia
.. _`Coverage report`: https://coveralls.io/r/Fantomas42/django-blog-zinnia
.. _`Google Group`: http://groups.google.com/group/django-blog-zinnia/
.. _`GitHub Issues`: https://github.com/Fantomas42/django-blog-zinnia/issues/
.. _`Vidzor Studio LLC`: http://vidzor.com/blog/
