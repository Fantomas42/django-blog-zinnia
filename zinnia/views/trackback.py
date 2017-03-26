"""Views for Zinnia trackback"""
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

import django_comments as comments

from zinnia.flags import TRACKBACK
from zinnia.flags import get_user_flagger
from zinnia.models.entry import Entry
from zinnia.signals import trackback_was_posted
from zinnia.spam_checker import check_is_spam


class EntryTrackback(TemplateView):
    """
    View for handling trackbacks on the entries.
    """
    content_type = 'text/xml'
    template_name = 'zinnia/entry_trackback.xml'

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        Decorate the view dispatcher with csrf_exempt.
        """
        return super(EntryTrackback, self).dispatch(*args, **kwargs)

    def get_object(self):
        """
        Retrieve the Entry trackbacked.
        """
        return get_object_or_404(Entry.published, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        """
        GET only do a permanent redirection to the Entry.
        """
        entry = self.get_object()
        return HttpResponsePermanentRedirect(entry.get_absolute_url())

    def post(self, request, *args, **kwargs):
        """
        Check if an URL is provided and if trackbacks
        are enabled on the Entry.
        If so the URL is registered one time as a trackback.
        """
        url = request.POST.get('url')

        if not url:
            return self.get(request, *args, **kwargs)

        entry = self.get_object()
        site = Site.objects.get_current()

        if not entry.trackbacks_are_open:
            return self.render_to_response(
                {'error': 'Trackback is not enabled for %s' % entry.title})

        title = request.POST.get('title') or url
        excerpt = request.POST.get('excerpt') or title
        blog_name = request.POST.get('blog_name') or title
        ip_address = request.META.get('REMOTE_ADDR', None)

        trackback_klass = comments.get_model()
        trackback_datas = {
            'content_type': ContentType.objects.get_for_model(Entry),
            'object_pk': entry.pk,
            'site': site,
            'user_url': url,
            'user_name': blog_name,
            'ip_address': ip_address,
            'comment': excerpt
        }

        trackback = trackback_klass(**trackback_datas)
        if check_is_spam(trackback, entry, request):
            return self.render_to_response(
                {'error': 'Trackback considered like spam'})

        trackback_defaults = {'comment': trackback_datas.pop('comment')}
        trackback, created = trackback_klass.objects.get_or_create(
            defaults=trackback_defaults,
            **trackback_datas)
        if created:
            trackback.flags.create(user=get_user_flagger(), flag=TRACKBACK)
            trackback_was_posted.send(trackback.__class__,
                                      trackback=trackback,
                                      entry=entry)
        else:
            return self.render_to_response(
                {'error': 'Trackback is already registered'})
        return self.render_to_response({})
