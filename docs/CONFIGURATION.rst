List of settings
================

Zinnia has several parameters to configure the application according to your needs.

All settings described here can be found in zinnia/settings.py

ZINNIA_PAGINATION
  **Default :** 10

  Integer used to paginate the entries.

ZINNIA_COPYRIGHT
  **Default :** 'Zinnia'

  String used for copyrighting the RSS feeds. 

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

ZINNIA_PING_DIRECTORIES 
  **Default :** ()

  List of the directories you want to ping.

ZINNIA_AUTO_PING
  **Default :** bool(ZINNIA_PING_DIRECTORIES)

  Boolean setting for telling if you want to ping directories when saving an entry.

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

ZINNIA_PLUGINS_TEMPLATES
  **Default :** ()

  List of tuple for extending the cms's plugins rendering templates.

