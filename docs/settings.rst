================
List of settings
================

.. module:: zinnia.settings

Zinnia has a lot of parameters to configure the application accordingly to
your needs. Knowing this list of settings can save you a lot of time.

Here's a full list of all available settings, and their default values.

All settings described here can be found in :file:`zinnia/settings.py`.

.. contents::
    :local:
    :depth: 1

.. _settings-entry:

Entry
=====

.. setting:: ZINNIA_ENTRY_TEMPLATES

ZINNIA_ENTRY_TEMPLATES
----------------------

Default value: ``()`` (Empty tuple)

List of tuple for extending the list of templates availables for
rendering the entry.

ZINNIA_ENTRY_BASE_MODEL
-----------------------
**Default value:** ``''``

String defining the base model path for the Entry model. See
:doc:`extending_entry_model` for more informations.

ZINNIA_UPLOAD_TO
----------------
**Default value:** ``'uploads'``

String setting that tells Zinnia where to upload entries' images.

.. _settings-edition:

Edition
=======

ZINNIA_MARKUP_LANGUAGE
----------------------
**Default value:** ``'html'``

String determining the markup language used for writing the entries.

ZINNIA_MARKDOWN_EXTENSIONS
--------------------------
**Default value:** ``''``

Extensions names to be used when rendering entries in MarkDown.

ZINNIA_WYSIWYG
--------------
**Default value:** ``'tinymce' if in settings.INSTALLED_APPS else
'wymeditor' if ZINNIA_MARKUP_LANGUAGE is 'html'. If MarkDown,
Textile or reStructuredText are used, the value will be 'markitup'.``

Used for determining the WYSIWYG editor for editing an entry.
Can also be used for disabling the WYSIWYG functionnality.

.. _settings-views:

Views
=====

ZINNIA_PAGINATION
-----------------

**Default value:** ``10``

Integer used to paginate the entries.

ZINNIA_ALLOW_EMPTY
------------------
**Default value:** ``True``

Used for archives views, raise a 404 error if no entries are present at
the specified date.

ZINNIA_ALLOW_FUTURE
-------------------
**Default value:** ``True``

Used for allowing archives views in the future.

.. _settings-feeds:

Feeds
=====

ZINNIA_FEEDS_FORMAT
-------------------
**Default value:** ``'rss'``

String determining the format of the syndication feeds.
Use 'atom' for Atom feeds.

ZINNIA_FEEDS_MAX_ITEMS
----------------------
**Default value:** ``15``

Integer used to define the maximum items provided in the syndication feeds.

.. _settings-urls:

URLs
====

ZINNIA_PROTOCOL
---------------
**Default value:** ``'http'``

String representing the protocol of the site.

ZINNIA_MEDIA_URL
----------------
**Default value:** ``os.path.join(settings.MEDIA_URL, 'zinnia/')``

String of the URL that handles the media files of Zinnia.

.. _settings-comments:

Comment moderation
==================

ZINNIA_AUTO_MODERATE_COMMENTS
-----------------------------
**Default value:** ``False``

Determine if a new comment should be allowed to show up
immediately or should be marked non-public and await approval.

ZINNIA_AUTO_CLOSE_COMMENTS_AFTER
--------------------------------
**Default value:** ``None``

Determine the number of days where comments are open.

ZINNIA_MAIL_COMMENT_REPLY
-------------------------
**Default value:** ``False``

Boolean used for sending an email to comment's authors
when a new comment is posted.

ZINNIA_MAIL_COMMENT_AUTHORS
---------------------------
**Default value:** ``True``

Boolean used for sending an email to entry authors
when a new comment is posted.

ZINNIA_MAIL_COMMENT_NOTIFICATION_RECIPIENTS
-------------------------------------------
**Default value:** ``list of emails based on settings.MANAGERS``

List of emails used for sending a notification when a
new public comment has been posted.

ZINNIA_SPAM_CHECKER_BACKENDS
----------------------------
**Default value:** ``()``

List of strings representing the module path to a spam checker backend.

.. _settings-pinging:

Pinging
=======

ZINNIA_PING_DIRECTORIES
-----------------------
**Default value:** ``('http://django-blog-zinnia.com/xmlrpc/',)``

List of the directories you want to ping.

ZINNIA_PING_EXTERNAL_URLS
-------------------------
**Default value:** ``True``

Boolean setting for telling if you want to ping external URLs when saving
an entry.

ZINNIA_SAVE_PING_DIRECTORIES
----------------------------
**Default value:** ``bool(ZINNIA_PING_DIRECTORIES)``

Boolean setting for telling if you want to ping directories when saving
an entry.

ZINNIA_PINGBACK_CONTENT_LENGTH
------------------------------
**Default value:** ``300``

Size of the excerpt generated on pingback.

.. _settings-similarity:

Similarity
==========

ZINNIA_F_MIN
------------
**Default value:** ``0.1``

Float setting of the minimal word frequency for similar entries.

ZINNIA_F_MAX
------------
**Default value:** ``1.0``

Float setting of the minimal word frequency for similar entries.

.. _settings-misc:

Miscellaneous
=============

ZINNIA_COPYRIGHT
----------------
**Default value:** ``'Zinnia'``

String used for copyrighting the syndication feeds.

ZINNIA_STOP_WORDS
-----------------
**Default value:** ``See zinnia/settings.py``

List of common words excluded from the advanced search engine
to optimize the search querying and the results.

ZINNIA_URL_SHORTENER_BACKEND
----------------------------
**Default value:** ``'zinnia.url_shortener.backends.default'``

String representing the module path to the URL shortener backend.

ZINNIA_USE_TWITTER
------------------
**Default value:** ``True if python-twitter is in PYTHONPATH``

Boolean telling if Zinnia can use Twitter.

.. _settings-cms:

CMS
===

All the settings related to the CMS can be found in :file:`zinnia/plugins/settings.py`.

ZINNIA_APP_MENUS
----------------
**Default value:** ``('zinnia.plugins.menu.EntryMenu',
'zinnia.plugins.menu.CategoryMenu', 'zinnia.plugins.menu.TagMenu', 'zinnia.plugins.menu.AuthorMenu')``

List of strings representing the path to the Menu class provided for the
Zinnia AppHook.

ZINNIA_HIDE_ENTRY_MENU
----------------------
**Default value:** ``True``

Boolean used for displaying or not the entries in the EntryMenu object.

ZINNIA_PLUGINS_TEMPLATES
------------------------
**Default value:** ``()``

List of tuple for extending the CMS's plugins rendering templates.
