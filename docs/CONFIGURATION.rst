List of settings
================

Zinnia has several parameters to configure the application according to your needs.

All settings described here can be found in zinnia/settings.py

ZINNIA_PAGINATION
  **Default :** 10

  Integer used to paginate the entries.

ZINNIA_ALLOW_EMPTY
  **Default :** True

  Used for archives views, raise a 404 error if no entries are present at the specified date.

ZINNIA_ALLOW_FUTURE
  **Default :** True

  Used for allowing archives views in the future.

ZINNIA_FEEDS_FORMAT
  **Default :** 'rss'

  String determining the format of the syndication feeds.
  Use 'atom' for Atom feeds.

ZINNIA_COPYRIGHT
  **Default :** 'Zinnia'

  String used for copyrighting the syndication feeds. 

ZINNIA_UPLOAD_TO
  **Default :** 'uploads'

  String setting that tells Zinnia where to upload entries' images.

ZINNIA_MEDIA_URL
  **Default :** '/zinnia/'

  String of the url that handles the media files of Zinnia.

ZINNIA_MAIL_COMMENT
  **Default :** True

  Boolean used for sending an email when a comment is posted or not.

ZINNIA_AKISMET_COMMENT
  **Default :** True

  Boolean used for protecting your comments with Akismet or not.

ZINNIA_FIRST_WEEK_DAY
  **Default :** 0

  Integer for setting the first day of the week in the Calendar widget. Ex : use 6 for Sunday.

ZINNIA_PING_DIRECTORIES 
  **Default :** ()

  List of the directories you want to ping.

ZINNIA_AUTO_PING
  **Default :** bool(ZINNIA_PING_DIRECTORIES)

  Boolean setting for telling if you want to ping directories when saving an entry.

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

