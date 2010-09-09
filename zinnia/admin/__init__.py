"""Admin of Zinnia"""
from django.contrib import admin

from zinnia.models import Entry
from zinnia.models import Category
from zinnia.admin.entry import EntryAdmin
from zinnia.admin.category import CategoryAdmin


admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
