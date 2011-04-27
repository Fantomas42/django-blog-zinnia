List of settings
================

Zinnia has several parameters to configure the application according to
your needs.

All settings described here can be found in zinnia/settings.py

ZINNIA_PAGINATION
  **Default :** 10

  Integer used to paginate the entries.

ZINNIA_ALLOW_EMPTY
  **Default :** True

  Used for archives views, raise a 404 error if no entries are present at
  the specified date.

ZINNIA_ALLOW_FUTURE
  **Default :** True

  Used for allowing archives views in the future.

ZINNIA_ENTRY_TEMPLATES
  **Default :** ()

  List of tuple for extending the list of templates availables for
  rendering the entry.

ZINNIA_ENTRY_BASE_MODEL
  **Default :** ''

  String defining the base Model path for the Entry model. See
  TODO_REF for more informations.

ZINNIA_MARKUP_LANGUAGE
  **Default :** 'html'

  String determining the markup language used for writing the entries.

ZINNIA_MARKDOWN_EXTENSIONS
  **Default :** ''

  Extensions names to be used when rendering entries in MarkDown.

ZINNIA_WYSIWYG
  **Default :** 'tinymce' if in settings.INSTALLED_APPS else 'wymeditor'
  if ZINNIA_MARKUP_LANGUAGE is 'html'. If MarkDown, Textile or reStructuredText
  are used, the value will be 'markitup'.

  Used for determining the WYSIWYG editor for editing an entry.
  Can also be used for disabling the WYSIWYG functionnality.

ZINNIA_FEEDS_FORMAT
  **Default :** 'rss'

  String determining the format of the syndication feeds.
  Use 'atom' for Atom feeds.

ZINNIA_FEEDS_MAX_ITEMS
  **Default :** 15

  Integer used to define the maximum items provided in the syndication feeds.

ZINNIA_COPYRIGHT
  **Default :** 'Zinnia'

  String used for copyrighting the syndication feeds.

ZINNIA_UPLOAD_TO
  **Default :** 'uploads'

  String setting that tells Zinnia where to upload entries' images.

ZINNIA_PROTOCOL
  **Default :** 'http'

  String representing the protocol of the site.

ZINNIA_MEDIA_URL
  **Default :** os.path.join(settings.MEDIA_URL, 'zinnia/')

  String of the url that handles the media files of Zinnia.

ZINNIA_AUTO_CLOSE_COMMENTS_AFTER
  **Default :** None

  Determine the number of days where comments are open.

ZINNIA_AUTO_MODERATE_COMMENTS
  **Default :** False

  Determine if a new comment should be allowed to show up
  immediately or should be marked non-public and await approval.

ZINNIA_MAIL_COMMENT_NOTIFICATION_RECIPIENTS
  **Default :** list of emails based on settings.MANAGERS

  List of emails used for sending a notification when a
  new public comment has been posted.

ZINNIA_MAIL_COMMENT_AUTHORS
  **Default :** True

  Boolean used for sending an email to entry authors
  when a new comment is posted.

ZINNIA_MAIL_COMMENT_REPLY
  **Default :** False

  Boolean used for sending an email to comment's authors
  when a new comment is posted.

ZINNIA_URL_SHORTENER_BACKEND
  **Default :** 'zinnia.url_shortener.backends.default'

  String representing the module path to the url shortener backend.

ZINNIA_STOP_WORDS
  **Default :** See zinnia/settings.py

  List of common words excluded from the advanced search engine
  to optimize the search querying and the results.

ZINNIA_AKISMET_COMMENT
  **Default :** True

  Boolean used for protecting your comments with Akismet or not.

ZINNIA_PING_DIRECTORIES
  **Default :** ('http://django-blog-zinnia.com/xmlrpc/',)

  List of the directories you want to ping.

ZINNIA_SAVE_PING_DIRECTORIES
  **Default :** bool(ZINNIA_PING_DIRECTORIES)

  Boolean setting for telling if you want to ping directories when saving
  an entry.

ZINNIA_PING_EXTERNAL_URLS
  **Default :** True

  Boolean setting for telling if you want to ping external urls when saving
  an entry.

ZINNIA_PINGBACK_CONTENT_LENGTH
  **Default :**	300

  Size of the excerpt generated on pingback.

ZINNIA_F_MIN
  **Default :** 0.1

  Float setting of the minimal word frequency for similar entries.

ZINNIA_F_MAX
  **Default :** 1.0

  Float setting of the minimal word frequency for similar entries.

ZINNIA_USE_BITLY
  **Default :** 'django_bitly' in settings.INSTALLED_APPS

  Boolean telling if Zinnia can use Bit.ly.

ZINNIA_USE_TWITTER
  **Default :** True if python-twitter is in PYTHONPATH

  Boolean telling if Zinnia can use Twitter.

CMS settings
------------

ZINNIA_PLUGINS_TEMPLATES
  **Default :** ()

  List of tuple for extending the CMS's plugins rendering templates.

ZINNIA_APP_MENUS
  **Default :** (EntryMenu, CategoryMenu, TagMenu, AuthorMenu)

  List of Menu objects provided for the Zinnia AppHook.

ZINNIA_HIDE_ENTRY_MENU
  **Default :** True

  Boolean used for displaying or not the entries in the EntryMenu object.
