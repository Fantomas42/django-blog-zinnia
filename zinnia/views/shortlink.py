"""Views for Zinnia shortlink"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from zinnia.models import Entry


def entry_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Entry,
    accordingly to 'object_id' argument
    """
    entry = get_object_or_404(Entry, pk=object_id)
    return redirect(entry, permanent=True)
