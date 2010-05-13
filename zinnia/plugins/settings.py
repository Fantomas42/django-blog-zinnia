"""Settings of Zinnia.plugins"""
from django.conf import settings

from zinnia.plugins.menu import EntryMenu
from zinnia.plugins.menu import TagMenu
from zinnia.plugins.menu import AuthorMenu
from zinnia.plugins.menu import CategoryMenu


APP_MENUS = getattr(settings, 'ZINNIA_APP_MENUS', [EntryMenu, CategoryMenu,
                                                   TagMenu, AuthorMenu])
PLUGINS_TEMPLATES = getattr(settings, 'ZINNIA_PLUGINS_TEMPLATES', [])


