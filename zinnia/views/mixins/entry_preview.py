"""Preview mixins for Zinnia views"""
from django.http import Http404
from django.utils.translation import ugettext as _

from zinnia.managers import PUBLISHED


class EntryPreviewMixin(object):
    """
    Mixin implementing the preview of Entries.
    """

    def get_object(self, queryset=None):
        """
        If the status of the entry is not PUBLISHED,
        a preview is requested, so we check if the user
        has the 'zinnia.can_view_all' permission or if
        it's an author of the entry.
        """
        obj = super(EntryPreviewMixin, self).get_object(queryset)
        if obj.status == PUBLISHED:
            return obj
        if (self.request.user.has_perm('zinnia.can_view_all') or
                self.request.user in obj.authors.all()):
            return obj
        raise Http404(_('No entry found matching the query'))
