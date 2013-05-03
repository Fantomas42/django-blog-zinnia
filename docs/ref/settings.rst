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

.. setting:: ZINNIA_ENTRY_BASE_MODEL

ZINNIA_ENTRY_BASE_MODEL
-----------------------
**Default value:** ``'zinnia.models_bases.entry.AbstractEntry'`` (Empty string)

String defining the base model path for the Entry model. See
:doc:`/how-to/extending_entry_model` for more informations.

.. setting:: ZINNIA_ENTRY_DETAIL_TEMPLATES

ZINNIA_ENTRY_DETAIL_TEMPLATES
-----------------------------
**Default value:** ``()`` (Empty tuple)

List of tuple for extending the list of templates availables for
rendering the entry detail view. By using this setting, you can
change the look and feel of an entry page directly in the admin
interface. Example: ::

  ZINNIA_ENTRY_DETAIL_TEMPLATES = (('entry_detail_alternate.html',
                                    gettext('Alternative template')),)

.. setting:: ZINNIA_ENTRY_CONTENT_TEMPLATES

ZINNIA_ENTRY_CONTENT_TEMPLATES
------------------------------
**Default value:** ``()`` (Empty tuple)

List of tuple for extending the list of templates availables for
rendering the content of an entry. By using this setting, you can
change the look and feel of an entry directly in the admin
interface. Example: ::

  ZINNIA_ENTRY_CONTENT_TEMPLATES = (('zinnia/_entry_detail_alternate.html',
                                     gettext('Alternative template')),)

.. setting:: ZINNIA_UPLOAD_TO

ZINNIA_UPLOAD_TO
----------------
**Default value:** ``'uploads/zinnia'``

String setting that tells Zinnia where to upload entries' images.

.. versionchanged:: 0.10

Previously the default value was ``'uploads'``.

.. _settings-edition:

Edition
=======

.. setting:: ZINNIA_MARKUP_LANGUAGE

ZINNIA_MARKUP_LANGUAGE
----------------------
**Default value:** ``'html'``

String determining the markup language used for writing the entries.
You can use one of these values: ::

    ['html', 'markdown', 'restructuredtext', 'textile']

The value of this variable will alter the value of :setting:`ZINNIA_WYSIWYG`
if you don't set it.

.. setting:: ZINNIA_MARKDOWN_EXTENSIONS

ZINNIA_MARKDOWN_EXTENSIONS
--------------------------
**Default value:** ``''`` (Empty string)

Extensions names to be used for rendering the entries in MarkDown. Example:
::

  ZINNIA_MARKDOWN_EXTENSIONS = 'extension1_name,extension2_name...'

.. setting:: ZINNIA_WYSIWYG

ZINNIA_WYSIWYG
--------------
**Default value:** ::

    WYSIWYG_MARKUP_MAPPING = {
        'textile': 'markitup',
        'markdown': 'markitup',
        'restructuredtext': 'markitup',
        'html': 'tinymce' in settings.INSTALLED_APPS and \
                    'tinymce' or 'wymeditor'}

    WYSIWYG = getattr(settings, 'ZINNIA_WYSIWYG',
                      WYSIWYG_MARKUP_MAPPING.get(ZINNIA_MARKUP_LANGUAGE))

Determining the WYSIWYG editor used for editing an entry.
So if MarkDown, Textile or reStructuredText are used, the value will be
``'markitup'``, but if you use HTML, TinyMCE will be used if
:ref:`django-tinymce is installed<zinnia-tinymce>`, else WYMEditor will be
used.

This setting can also be used for disabling the WYSIWYG
functionnality. Example: ::

  ZINNIA_WYSIWYG = None

.. _settings-views:

Views
=====

.. setting:: ZINNIA_PAGINATION

ZINNIA_PAGINATION
-----------------

**Default value:** ``10``

Integer used to paginate the entries. So by default you will have 10
entries displayed per page on the Weblog.

.. setting:: ZINNIA_ALLOW_EMPTY

ZINNIA_ALLOW_EMPTY
------------------
**Default value:** ``True``

Used for archives views, raise a 404 error if no entries are present at
a specified date.

.. setting:: ZINNIA_ALLOW_FUTURE

ZINNIA_ALLOW_FUTURE
-------------------
**Default value:** ``True``

Used for allowing archives views in the future.

.. _settings-feeds:

Feeds
=====

.. setting:: ZINNIA_FEEDS_FORMAT

ZINNIA_FEEDS_FORMAT
-------------------
**Default value:** ``'rss'``

String determining the format of the syndication feeds. You can use
``'atom'`` if your prefer Atom feeds.

.. setting:: ZINNIA_FEEDS_MAX_ITEMS

ZINNIA_FEEDS_MAX_ITEMS
----------------------
**Default value:** ``15``

Integer used to define the maximum items provided in the syndication feeds.
So by default you will have 15 entries displayed on the feeds.

.. _settings-urls:

URLs
====

.. setting:: ZINNIA_TRANSLATED_URLS

ZINNIA_TRANSLATED_URLS
----------------------
.. versionadded:: 0.12.2

**Default value:** ``False``

Boolean used to activate the internationalization of the URLs provided by
Zinnia if the translation is avaialable in your language.

.. setting:: ZINNIA_URL_SHORTENER_BACKEND

ZINNIA_URL_SHORTENER_BACKEND
----------------------------
**Default value:** ``'zinnia.url_shortener.backends.default'``

String representing the module path to the URL shortener backend.

.. setting:: ZINNIA_PROTOCOL

ZINNIA_PROTOCOL
---------------
**Default value:** ``'http'``

String representing the protocol of the site. If your Web site uses HTTPS,
set this setting to ``https``.

.. _settings-comments:

Comments
========

.. setting:: ZINNIA_AUTO_MODERATE_COMMENTS

ZINNIA_AUTO_MODERATE_COMMENTS
-----------------------------
**Default value:** ``False``

Determine if a new comment should be allowed to show up
immediately or should be marked non-public and await approval.

.. setting:: ZINNIA_AUTO_CLOSE_COMMENTS_AFTER

ZINNIA_AUTO_CLOSE_COMMENTS_AFTER
--------------------------------
**Default value:** ``None`` (forever)

Determine the number of days where comments are open. If you set this
setting to ``10`` the comments will be closed automaticaly 10 days after
the publication date of your entries.

``0`` means disabling comments completely.

.. setting:: ZINNIA_MAIL_COMMENT_REPLY

ZINNIA_MAIL_COMMENT_REPLY
-------------------------
**Default value:** ``False``

Boolean used for sending an email to comment's authors
when a new comment is posted.

.. setting:: ZINNIA_MAIL_COMMENT_AUTHORS

ZINNIA_MAIL_COMMENT_AUTHORS
---------------------------
**Default value:** ``True``

Boolean used for sending an email to entry authors
when a new comment is posted.

.. setting:: ZINNIA_MAIL_COMMENT_NOTIFICATION_RECIPIENTS

ZINNIA_MAIL_COMMENT_NOTIFICATION_RECIPIENTS
-------------------------------------------
**Default value:** ::

    [manager_tuple[1] for manager_tuple in settings.MANAGERS]

List of emails used for sending a notification when a
new public comment has been posted.

.. setting:: ZINNIA_SPAM_CHECKER_BACKENDS

ZINNIA_SPAM_CHECKER_BACKENDS
----------------------------
**Default value:** ``()`` (Empty tuple)

List of strings representing the module path to a spam checker backend.
See :doc:`/topics/spam_checker` for more informations about this setting.

.. setting:: ZINNIA_COMMENT_MIN_WORDS

ZINNIA_COMMENT_MIN_WORDS
------------------------
**Default value:** ``4``

Minimal number of words required to post a comment if
:func:`zinnia.spam_checker.backends.long_enough.backend` is enabled in
:setting:`ZINNIA_SPAM_CHECKER_BACKENDS`.

.. setting:: ZINNIA_DEFAULT_USER_ID

ZINNIA_COMMENT_FLAG_USER_ID
---------------------------
**Default value:** ``1``

The ID of the User to be used when flagging the comments as spam, pingback
or trackback.

.. _settings-linkbacks:

Linkbacks
=========

.. setting:: ZINNIA_AUTO_CLOSE_PINGBACKS_AFTER

ZINNIA_AUTO_CLOSE_PINGBACKS_AFTER
---------------------------------
**Default value:** ``None`` (forever)

Determine the number of days where pingbacks are open. If you set this
setting to ``10`` the pingbacks will be closed automaticaly 10 days after
the publication date of your entries.

``0`` means disabling pingbacks completely.

.. setting:: ZINNIA_AUTO_CLOSE_TRACKBACKS_AFTER

ZINNIA_AUTO_CLOSE_TRACKBACKS_AFTER
----------------------------------
**Default value:** ``None`` (forever)

Determine the number of days where trackbacks are open. If you set this
setting to ``10`` the trackbacks will be closed automaticaly 10 days after
the publication date of your entries.

``0`` means disabling trackbacks completely.

.. _settings-pinging:

Pinging
=======

.. setting:: ZINNIA_PING_DIRECTORIES

ZINNIA_PING_DIRECTORIES
-----------------------
**Default value:** ``('http://django-blog-zinnia.com/xmlrpc/',)``

List of the directories you want to ping.

.. setting:: ZINNIA_PING_EXTERNAL_URLS

ZINNIA_PING_EXTERNAL_URLS
-------------------------
**Default value:** ``True``

Boolean setting for telling if you want to ping external URLs when saving
an entry.

.. setting:: ZINNIA_SAVE_PING_DIRECTORIES

ZINNIA_SAVE_PING_DIRECTORIES
----------------------------
**Default value:** ``bool(ZINNIA_PING_DIRECTORIES)``

Boolean setting for telling if you want to ping directories when saving
an entry.

.. setting:: ZINNIA_PINGBACK_CONTENT_LENGTH

ZINNIA_PINGBACK_CONTENT_LENGTH
------------------------------
**Default value:** ``300``

Size of the excerpt generated on pingback.

.. _settings-similarity:

Similarity
==========

.. setting:: ZINNIA_F_MIN

ZINNIA_F_MIN
------------
**Default value:** ``0.1``

Float setting of the minimal word frequency for similar entries.

.. setting:: ZINNIA_F_MAX

ZINNIA_F_MAX
------------
**Default value:** ``1.0``

Float setting of the minimal word frequency for similar entries.

.. _settings-misc:

Miscellaneous
=============

.. setting:: ZINNIA_COPYRIGHT

ZINNIA_COPYRIGHT
----------------
**Default value:** ``'Zinnia'``

String used for copyrighting your entries, used in the syndication feeds
and in the opensearch document.

.. setting:: ZINNIA_STOP_WORDS

ZINNIA_STOP_WORDS
-----------------
**Default value:** See :file:`zinnia/settings.py`

List of common words excluded from the advanced search engine
to optimize the search querying and the results.

.. setting:: ZINNIA_USE_TWITTER

ZINNIA_USE_TWITTER
------------------
**Default value:** ``True if the crendentials of Twitter have been defined``

Boolean telling if the credentials of a Twitter account have been set and
if Zinnia can post on Twitter.
