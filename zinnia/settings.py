"""Settings of Zinnia"""
from django.conf import settings

PING_DIRECTORIES = getattr(settings, 'ZINNIA_PING_DIRECTORIES',
                           ('http://django-blog-zinnia.com/xmlrpc/',))
SAVE_PING_DIRECTORIES = getattr(settings, 'ZINNIA_SAVE_PING_DIRECTORIES',
                                bool(PING_DIRECTORIES))
SAVE_PING_EXTERNAL_URLS = getattr(settings, 'ZINNIA_PING_EXTERNAL_URLS', True)

TRANSLATED_URLS = getattr(settings, 'ZINNIA_TRANSLATED_URLS', False)

COPYRIGHT = getattr(settings, 'ZINNIA_COPYRIGHT', 'Zinnia')

PAGINATION = getattr(settings, 'ZINNIA_PAGINATION', 10)
ALLOW_EMPTY = getattr(settings, 'ZINNIA_ALLOW_EMPTY', True)
ALLOW_FUTURE = getattr(settings, 'ZINNIA_ALLOW_FUTURE', True)

ENTRY_BASE_MODEL = getattr(settings, 'ZINNIA_ENTRY_BASE_MODEL', '')
ENTRY_DETAIL_TEMPLATES = getattr(
    settings, 'ZINNIA_ENTRY_DETAIL_TEMPLATES', [])
ENTRY_CONTENT_TEMPLATES = getattr(
    settings, 'ZINNIA_ENTRY_CONTENT_TEMPLATES', [])

MARKUP_LANGUAGE = getattr(settings, 'ZINNIA_MARKUP_LANGUAGE', 'html')

MARKDOWN_EXTENSIONS = getattr(settings, 'ZINNIA_MARKDOWN_EXTENSIONS', '')

WYSIWYG_MARKUP_MAPPING = {
    'textile': 'markitup',
    'markdown': 'markitup',
    'restructuredtext': 'markitup',
    'html': 'tinymce' in settings.INSTALLED_APPS and 'tinymce' or 'wymeditor'}

WYSIWYG = getattr(settings, 'ZINNIA_WYSIWYG',
                  WYSIWYG_MARKUP_MAPPING.get(MARKUP_LANGUAGE))

AUTO_CLOSE_PINGBACKS_AFTER = getattr(
    settings, 'ZINNIA_AUTO_CLOSE_PINGBACKS_AFTER', None)

AUTO_CLOSE_TRACKBACKS_AFTER = getattr(
    settings, 'ZINNIA_AUTO_CLOSE_TRACKBACKS_AFTER', None)

AUTO_CLOSE_COMMENTS_AFTER = getattr(
    settings, 'ZINNIA_AUTO_CLOSE_COMMENTS_AFTER', None)

AUTO_MODERATE_COMMENTS = getattr(settings, 'ZINNIA_AUTO_MODERATE_COMMENTS',
                                 False)

MAIL_COMMENT_REPLY = getattr(settings, 'ZINNIA_MAIL_COMMENT_REPLY', False)

MAIL_COMMENT_AUTHORS = getattr(settings, 'ZINNIA_MAIL_COMMENT_AUTHORS', True)

MAIL_COMMENT_NOTIFICATION_RECIPIENTS = getattr(
    settings, 'ZINNIA_MAIL_COMMENT_NOTIFICATION_RECIPIENTS',
    [manager_tuple[1] for manager_tuple in settings.MANAGERS])

COMMENT_MIN_WORDS = getattr(settings, 'ZINNIA_COMMENT_MIN_WORDS', 4)

COMMENT_FLAG_USER_ID = getattr(settings, 'ZINNIA_COMMENT_FLAG_USER_ID', 1)

UPLOAD_TO = getattr(settings, 'ZINNIA_UPLOAD_TO', 'uploads/zinnia')

PROTOCOL = getattr(settings, 'ZINNIA_PROTOCOL', 'http')

FEEDS_FORMAT = getattr(settings, 'ZINNIA_FEEDS_FORMAT', 'rss')
FEEDS_MAX_ITEMS = getattr(settings, 'ZINNIA_FEEDS_MAX_ITEMS', 15)

PINGBACK_CONTENT_LENGTH = getattr(settings,
                                  'ZINNIA_PINGBACK_CONTENT_LENGTH', 300)

F_MIN = getattr(settings, 'ZINNIA_F_MIN', 0.1)
F_MAX = getattr(settings, 'ZINNIA_F_MAX', 1.0)

SPAM_CHECKER_BACKENDS = getattr(settings, 'ZINNIA_SPAM_CHECKER_BACKENDS',
                                ())

URL_SHORTENER_BACKEND = getattr(settings, 'ZINNIA_URL_SHORTENER_BACKEND',
                                'zinnia.url_shortener.backends.default')

STOP_WORDS = getattr(settings, 'ZINNIA_STOP_WORDS',
                     ('able', 'about', 'across', 'after', 'all', 'almost',
                      'also', 'among', 'and', 'any', 'are', 'because', 'been',
                      'but', 'can', 'cannot', 'could', 'dear', 'did', 'does',
                      'either', 'else', 'ever', 'every', 'for', 'from', 'get',
                      'got', 'had', 'has', 'have', 'her', 'hers', 'him', 'his',
                      'how', 'however', 'into', 'its', 'just', 'least', 'let',
                      'like', 'likely', 'may', 'might', 'most', 'must',
                      'neither', 'nor', 'not', 'off', 'often', 'only', 'other',
                      'our', 'own', 'rather', 'said', 'say', 'says', 'she',
                      'should', 'since', 'some', 'than', 'that', 'the',
                      'their', 'them', 'then', 'there', 'these', 'they',
                      'this', 'tis', 'too', 'twas', 'wants', 'was', 'were',
                      'what', 'when', 'where', 'which', 'while', 'who', 'whom',
                      'why', 'will', 'with', 'would', 'yet', 'you', 'your'))

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
TWITTER_ACCESS_KEY = getattr(settings, 'TWITTER_ACCESS_KEY', '')
TWITTER_ACCESS_SECRET = getattr(settings, 'TWITTER_ACCESS_SECRET', '')

USE_TWITTER = getattr(settings, 'ZINNIA_USE_TWITTER',
                      bool(TWITTER_ACCESS_KEY and TWITTER_ACCESS_SECRET and
                           TWITTER_CONSUMER_KEY and TWITTER_CONSUMER_SECRET))
