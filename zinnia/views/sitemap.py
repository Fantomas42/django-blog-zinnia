"""Views for Zinnia sitemap"""
from django.views.generic import TemplateView

from zinnia.models.entry import Entry
from zinnia.models.category import Category


class Sitemap(TemplateView):
    """Sitemap view of the blog"""
    template_name = 'zinnia/sitemap.html'

    def get_context_data(self, **kwargs):
        """Populate the context of the template
        with all published entries and all the categories"""
        context = super(Sitemap, self).get_context_data(**kwargs)
        context.update({'entries': Entry.published.all(),
                        'categories': Category.objects.all()})
        return context
