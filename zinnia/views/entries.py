"""Views for Zinnia entries"""
from django.views.generic.dates import BaseDateDetailView

from zinnia.models import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin
from zinnia.views.mixins.templates import EntryArchiveTemplateResponseMixin


class EntryDateDetail(ArchiveMixin,
                      EntryArchiveTemplateResponseMixin,
                      BaseDateDetailView):
    """
    Mixin combinating:

    - ArchiveMixin configuration centralizing conf for archive views
    - EntryArchiveTemplateResponseMixin to provide a
      custom templates depending on the date
    - BaseDateDetailView to retrieve the entry with date and slug
    """
    queryset = Entry.published.on_site()


class EntryDetail(EntryProtectionMixin, EntryDateDetail):
    """Detailled view archive view for an Entry
    with password and login protections"""
