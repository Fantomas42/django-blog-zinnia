"""Views for Zinnia entries"""
from django.views.generic.dates import BaseDateDetailView

from zinnia.models.entry import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.templates import EntryArchiveTemplateResponseMixin
from zinnia.views.mixins.tz_fixes import EntryDateDetailTZFix


class EntryDateDetail(EntryDateDetailTZFix,
                      ArchiveMixin,
                      EntryArchiveTemplateResponseMixin,
                      CallableQuerysetMixin,
                      BaseDateDetailView):
    """
    Mixin combinating:

    - ArchiveMixin configuration centralizing conf for archive views
    - EntryArchiveTemplateResponseMixin to provide a
      custom templates depending on the date
    - BaseDateDetailView to retrieve the entry with date and slug
    - CallableQueryMixin to defer the execution of the *queryset*
      property when imported
    - EntryDateDetailTZFix for handing the time-zones correctly
      in Django 1.4.
    """
    queryset = Entry.published.on_site


class EntryDetail(EntryProtectionMixin, EntryDateDetail):
    """Detailled view archive view for an Entry
    with password and login protections"""
