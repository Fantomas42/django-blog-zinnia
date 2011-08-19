"""Settings of Zinnia.plugins"""
from django.conf import settings
import sys 

HIDE_ENTRY_MENU = getattr(settings, 'ZINNIA_HIDE_ENTRY_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'ZINNIA_PLUGINS_TEMPLATES', [])
try:

    APP_STRING_LIST = getattr(settings, 'ZINNIA_APP_MENUS', ["EntryMenu", "CategoryMenu",
                                                       "TagMenu", "AuthorMenu"])
    APP_MENUS = []
    for app_string in APP_STRING_LIST:
        if "." in app_string:
            __import__(".".join(app_string.split(".")[:-1]), globals(), locals())
            module = sys.modules[".".join(app_string.split(".")[:-1])]
            app = app_string.split(".")[-1]
        else:
            from zinnia.plugins import menu
            app = app_string
            module = menu
        APP_MENUS.append(getattr(module, app))
except ImportError:
    APP_MENUS = []
