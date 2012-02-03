"""Views for Zinnia archives"""
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day

from zinnia.models import Entry
from zinnia.views.decorators import update_queryset


entry_index = update_queryset(object_list, Entry.published.all)

entry_year = update_queryset(archive_year, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)
