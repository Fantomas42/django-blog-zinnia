"""Admin of Zinnia"""
from django.contrib import admin

import swapper

from zinnia.admin.category import CategoryAdmin
from zinnia.admin.entry import EntryAdmin
from zinnia.models.category import Category


Entry = swapper.load_model("zinnia", "Entry")

admin.site.register(Entry, EntryAdmin)
admin.site.register(Category, CategoryAdmin)
