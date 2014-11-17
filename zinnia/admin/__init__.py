"""Admin of Zinnia"""
from django.contrib import admin

from zinnia.models.entry import Entry
from zinnia.models.category import Category
from zinnia.admin.entry import EntryAdmin
from zinnia.admin.category import CategoryAdmin
from zinnia.settings import ENTRY_BASE_MODEL


if ENTRY_BASE_MODEL == 'zinnia.models_bases.entry.AbstractEntry':
    admin.site.register(Entry, EntryAdmin)

admin.site.register(Category, CategoryAdmin)
