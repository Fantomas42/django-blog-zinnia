"""Views for Zinnia entries"""
from django.views.generic.dates import DateDetailView

from zinnia.models import Entry
from zinnia.views.mixins import ArchiveMixin
from zinnia.views.mixins import EntryProtectionMixin


class EntryDateDetail(ArchiveMixin, DateDetailView):
    """Base detailled archive view for an Entry"""
    queryset = Entry.published.on_site()
    template_name_field = 'template'


class EntryDetail(EntryProtectionMixin, EntryDateDetail):
    """Detailled view archive view for an Entry
    with password and login protections"""
