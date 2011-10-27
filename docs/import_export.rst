===============
Import / Export
===============

.. highlightlang:: console

If you already have a blog, Zinnia has the ability to import your posts
from other blogging platforms. Useful for rapid migration.

.. _wordpress2zinnia:

From WordPress to Zinnia
========================

Zinnia provides a command for importing export files from WordPress.

http://codex.wordpress.org/Tools_Export_SubPanel

Once you have the XML file, you simply have to do this. ::

  $ python manage.py wp2zinnia path/to/your/wordpress.xml

This command will associate the post's authors to User and
import the tags, categories, post and comments.

For the options execute this. ::

  $ python manage.py help wp2zinnia

.. _zinnia2wordpress:

From Zinnia to WordPress
========================

Zinnia also provides a command for exporting your blog to WordPress in the
case you want to migrate on it.

Simply execute this command: ::

  $ python manage.py zinnia2wp > export.xml

Once you have the XML export, you can import it into your WordPress site.

http://codex.wordpress.org/Importing_Content

.. _blogger2zinnia:

From Blogger to Zinnia
======================

If you are comming from Blogger, you can import your posts and comments
with this simple command: ::

  $ python manage.py blogger2zinnia

For the options execute this. ::

  $ python manage.py help blogger2zinnia

Note that you need to install the `gdata`_ package to run the importation.

.. _feed2zinnia:

From Feed to Zinnia
===================

If you don't have the possibility to export your posts but have a RSS or Atom
feed on your Weblog, Zinnia can import it. This command is the most generic
way to import content into Zinnia. Simply execute this command: ::

  $ python manage.py feed2zinnia http://url.of/the/feed

For the options execute this. ::

  $ python manage.py help feed2zinnia

Note that you need to install the `feedparser`_ package to run the
importation.


.. _`gdata`: https://code.google.com/p/gdata-python-client/
.. _`feedparser`: https://code.google.com/p/feedparser/
