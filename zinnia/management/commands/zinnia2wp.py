"""Zinnia to WordPress command module"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

from tagging.models import Tag

from zinnia import __version__
from zinnia.settings import PROTOCOL
from zinnia.models.entry import Entry
from zinnia.models.category import Category


class Command(NoArgsCommand):
    """Command object for exporting a Zinnia blog
    into WordPress via a WordPress eXtended RSS (WXR) file."""
    help = 'Export Zinnia to WXR file.'

    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        blog_context = {'entries': Entry.objects.all(),
                        'categories': Category.objects.all(),
                        'tags': Tag.objects.usage_for_model(Entry),
                        'version': __version__,
                        'language': settings.LANGUAGE_CODE,
                        'site': site,
                        'site_url': '%s://%s' % (PROTOCOL, site.domain)}
        export = render_to_string('zinnia/wxr.xml', blog_context)
        print smart_str(export)
