"""Views for Zinnia entries"""
from django.views.generic.dates import DateDetailView

from zinnia.models import Entry
from zinnia.views.mixins import ArchiveMixin


class EntryDetail(ArchiveMixin, DateDetailView):
    """Detailled view for an Entry"""
    queryset = Entry.published.on_site()
