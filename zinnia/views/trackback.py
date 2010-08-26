"""Views for zinnia trackback"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template

from zinnia.models import Entry


def entry_trackback(request, slug):
    """Set a TrackBack for an Entry"""    
    entry = get_object_or_404(Entry.published, slug=slug)
    
    if request.POST.get('url'):
        error = ''
        url = request.POST['url']
        site = Site.objects.get_current()
        
        if not entry.pingback_enabled:
            error = u'Trackback is not enabled for %s' % entry.title
        
        title = request.POST.get('title') or url
        excerpt = request.POST.get('excerpt') or title
        blog_name = request.POST.get('blog_name') or title

        if not error:
            comment, created = Comment.objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Entry),
                object_pk=entry.pk, user_url=url, site=site,
                defaults={'comment': excerpt, 'user_name': blog_name})
            if created:
                user = entry.authors.all()[0]
                comment.flags.create(user=user, flag='trackback')
            else:
                error = u'Trackback is already registered'

        return direct_to_template(request, 'zinnia/entry_trackback.xml',
                                  mimetype='text/xml',
                                  extra_context={'error': error})
    
    return redirect(entry)
