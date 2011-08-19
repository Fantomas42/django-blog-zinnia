"""Settings of Zinnia.plugins"""
import warnings

from django.conf import settings
from django.utils.importlib import import_module


HIDE_ENTRY_MENU = getattr(settings, 'ZINNIA_HIDE_ENTRY_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'ZINNIA_PLUGINS_TEMPLATES', [])


APP_MENUS = []
DEFAULT_APP_MENUS = ['zinnia.plugins.menu.EntryMenu',
                     'zinnia.plugins.menu.CategoryMenu',
                     'zinnia.plugins.menu.TagMenu',
                     'zinnia.plugins.menu.AuthorMenu']

for menu_string in getattr(settings, 'ZINNIA_APP_MENUS', DEFAULT_APP_MENUS):
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        APP_MENUS.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)
