"""Settings of Zinnia"""
from django.conf import settings

from mots_vides import stop_words


PING_DIRECTORIES = getattr(settings, 'ZINNIA_PING_DIRECTORIES',
                           ('https://django-blog-zinnia.com/xmlrpc/',))
SAVE_PING_DIRECTORIES = getattr(settings, 'ZINNIA_SAVE_PING_DIRECTORIES',
                                bool(PING_DIRECTORIES))
SAVE_PING_EXTERNAL_URLS = getattr(settings, 'ZINNIA_PING_EXTERNAL_URLS', True)

TRANSLATED_URLS = getattr(settings, 'ZINNIA_TRANSLATED_URLS', False)

COPYRIGHT = getattr(settings, 'ZINNIA_COPYRIGHT', 'Zinnia')

PAGINATION = getattr(settings, 'ZINNIA_PAGINATION', 10)
ALLOW_EMPTY = getattr(settings, 'ZINNIA_ALLOW_EMPTY', True)
ALLOW_FUTURE = getattr(settings, 'ZINNIA_ALLOW_FUTURE', True)

ENTRY_BASE_MODEL = getattr(settings, 'ZINNIA_ENTRY_BASE_MODEL',
                           'zinnia.models_bases.entry.AbstractEntry')

ENTRY_DETAIL_TEMPLATES = getattr(
    settings, 'ZINNIA_ENTRY_DETAIL_TEMPLATES', [])
ENTRY_CONTENT_TEMPLATES = getattr(
    settings, 'ZINNIA_ENTRY_CONTENT_TEMPLATES', [])
ENTRY_LOOP_TEMPLATES = getattr(
    settings, 'ZINNIA_ENTRY_LOOP_TEMPLATES', {})
ENTRY_LOOP_TEMPLATES.setdefault('default', {})

MARKUP_LANGUAGE = getattr(settings, 'ZINNIA_MARKUP_LANGUAGE', 'html')

MARKDOWN_EXTENSIONS = getattr(settings, 'ZINNIA_MARKDOWN_EXTENSIONS', [])

RESTRUCTUREDTEXT_SETTINGS = getattr(
    settings, 'ZINNIA_RESTRUCTUREDTEXT_SETTINGS', {})

PREVIEW_SPLITTERS = getattr(settings, 'ZINNIA_PREVIEW_SPLITTERS',
                            ['<!-- more -->', '<!--more-->'])

PREVIEW_MAX_WORDS = getattr(settings, 'ZINNIA_PREVIEW_MAX_WORDS', 55)

PREVIEW_MORE_STRING = getattr(settings, 'ZINNIA_PREVIEW_MORE_STRING', ' ...')

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

SEARCH_FIELDS = getattr(settings, 'ZINNIA_SEARCH_FIELDS',
                        ['title', 'lead', 'content',
                         'excerpt', 'image_caption', 'tags'])

COMPARISON_FIELDS = getattr(settings, 'ZINNIA_COMPARISON_FIELDS',
                            ['title', 'lead', 'content',
                             'excerpt', 'image_caption', 'tags'])

SPAM_CHECKER_BACKENDS = getattr(settings, 'ZINNIA_SPAM_CHECKER_BACKENDS',
                                [])

URL_SHORTENER_BACKEND = getattr(settings, 'ZINNIA_URL_SHORTENER_BACKEND',
                                'zinnia.url_shortener.backends.default')

STOP_WORDS = stop_words(settings.LANGUAGE_CODE.split('-')[0])
