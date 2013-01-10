"""Views for Zinnia quick entry"""
from urllib import urlencode

from django import forms
from django.shortcuts import redirect
from django.utils.html import linebreaks
from django.views.generic.base import View
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.utils import timezone

from zinnia.models.entry import Entry
from zinnia.managers import DRAFT
from zinnia.managers import PUBLISHED


class QuickEntryForm(forms.ModelForm):
    """Form for posting an entry quickly"""

    class Meta:
        model = Entry
        exclude = ('comment_count',
                   'pingback_count',
                   'trackback_count')


class QuickEntry(View):
    """View handling the quick post of a short Entry"""

    @method_decorator(permission_required('zinnia.add_entry'))
    def dispatch(self, *args, **kwargs):
        """Decorate the view dispatcher with permission_required"""
        return super(QuickEntry, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """GET only do a redirection to the admin for adding and entry"""
        return redirect('admin:zinnia_entry_add')

    def post(self, request, *args, **kwargs):
        """Handle the datas for posting a quick entry,
        and redirect to the admin in case of error or
        to the entry's page in case of success"""
        data = {
            'title': request.POST.get('title'),
            'slug': slugify(request.POST.get('title')),
            'status': DRAFT if 'save_draft' in request.POST else PUBLISHED,
            'sites': [Site.objects.get_current().pk],
            'authors': [request.user.pk],
            'content_template': 'zinnia/_entry_detail.html',
            'detail_template': 'entry_detail.html',
            'creation_date': timezone.now(),
            'last_update': timezone.now(),
            'content': request.POST.get('content'),
            'tags': request.POST.get('tags')}
        form = QuickEntryForm(data)
        if form.is_valid():
            form.instance.content = linebreaks(form.cleaned_data['content'])
            entry = form.save()
            return redirect(entry)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:zinnia_entry_add'),
                                   urlencode(data)))
