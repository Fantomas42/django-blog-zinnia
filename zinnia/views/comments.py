"""Views for Zinnia comments"""
from django.contrib import comments
from django.template.defaultfilters import slugify
from django.http import HttpResponsePermanentRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.views.generic.base import TemplateResponseMixin


class CommentSuccess(TemplateResponseMixin, View):
    """View for handing the publication of a Comment
    on an Entry. Do a redirection if the comment is visible,
    else render a confirmation template."""
    template_name = 'comments/zinnia/entry/posted.html'

    def get_context_data(self, **kwargs):
        return {'comment': self.comment}

    def get(self, request, *args, **kwargs):
        self.comment = None

        if 'c' in request.GET:
            try:
                self.comment = comments.get_model().objects.get(
                    pk=request.GET['c'])
            except ObjectDoesNotExist:
                pass
        if self.comment and self.comment.is_public:
            return HttpResponsePermanentRedirect(
                self.comment.get_absolute_url(
                    '#comment-%(id)s-by-') + slugify(self.comment.user_name))

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
