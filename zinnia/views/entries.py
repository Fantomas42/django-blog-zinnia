"""Views for zinnia entries"""
from django.contrib.auth.views import login
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from zinnia.models import Entry
from zinnia.views.decorators import update_queryset


entry_index = update_queryset(object_list, Entry.published.all)

entry_year = update_queryset(archive_year, Entry.published.all)

entry_month = update_queryset(archive_month, Entry.published.all)

entry_day = update_queryset(archive_day, Entry.published.all)

def entry_detail(request, *ka, **kw):
    """Perform a security check around object_detail"""
    entry = get_object_or_404(Entry, slug=kw['slug'],
                              creation_date__year=kw['year'],
                              creation_date__month=kw['month'],
                              creation_date__day=kw['day'])
    
    if entry.login_required and not request.user.is_authenticated():
        return login(request, 'zinnia/login.html')
#    if entry.password and not request.session.has_key('zinnia_entry_%s' % entry.pk)
#      Do some stuff
    return object_detail(request, *ka, **kw)
