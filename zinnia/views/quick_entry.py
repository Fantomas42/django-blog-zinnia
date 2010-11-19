"""Views for Zinnia quick entry"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from zinnia.models import Entry
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED


class QuickEntryForm(forms.Form):
    """Form for posting an entry quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('zinnia.add_entry')
def view_quick_entry(request):
    """View for quickly post an Entry"""
    if request.POST:
        form = QuickEntryForm(request.POST)
        if form.is_valid():
            entry_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            entry_dict['content'] = linebreaks(entry_dict['content'])
            entry_dict['slug'] = slugify(entry_dict['title'])
            entry_dict['status'] = status
            entry = Entry.objects.create(**entry_dict)
            entry.sites.add(Site.objects.get_current())
            entry.authors.add(request.user)
            return redirect(entry)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get('content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:zinnia_entry_add'),
                                   urlencode(data)))

    return redirect('admin:zinnia_entry_add')
