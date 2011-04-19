"""Decorators for zinnia.views"""
from functools import wraps

from django.template import RequestContext
from django.contrib.auth.views import login
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from zinnia.models import Entry


def update_queryset(view, queryset,
                    queryset_parameter='queryset'):
    """Decorator around views based on a queryset
    passed in parameter, who will force the update
    of the queryset before executing the view.
    Related to issue http://code.djangoproject.com/ticket/8378"""

    @wraps(view)
    def wrapper(*args, **kwargs):
        """Regenerate the queryset before passing it to the view."""
        kwargs[queryset_parameter] = queryset()
        return view(*args, **kwargs)

    return wrapper


@csrf_protect
@never_cache
def password(request, entry):
    """Displays the password form and handle validation
    by setting the valid password in a cookie."""
    error = False
    if request.method == 'POST':
        if request.POST.get('password') == entry.password:
            request.session[
                'zinnia_entry_%s_password' % entry.pk] = entry.password
            return redirect(entry)
        error = True
    return render_to_response('zinnia/password.html', {'error': error},
                              context_instance=RequestContext(request))


def protect_entry(view):
    """Decorator performing a security check if needed
    around the generic.date_based.entry_detail view
    and specify the template used to render the entry"""

    @wraps(view)
    def wrapper(*ka, **kw):
        """Do security check and retrieve the template"""
        request = ka[0]
        entry = get_object_or_404(Entry, slug=kw['slug'],
                                  creation_date__year=kw['year'],
                                  creation_date__month=kw['month'],
                                  creation_date__day=kw['day'])

        if entry.login_required and not request.user.is_authenticated():
            return login(request, 'zinnia/login.html')
        if entry.password and entry.password != \
               request.session.get('zinnia_entry_%s_password' % entry.pk):
            return password(request, entry)
        kw['template_name'] = entry.template
        return view(*ka, **kw)

    return wrapper


def template_name_for_entry_queryset_filtered(model_type, model_name):
    """Return a custom template name for views
    returning a queryset of Entry filtered by another model."""
    template_name_list = (
        'zinnia/%s/%s/entry_list.html' % (model_type, model_name),
        'zinnia/%s/%s_entry_list.html' % (model_type, model_name),
        'zinnia/%s/entry_list.html' % model_type,
        'zinnia/entry_list.html')

    for template_name in template_name_list:
        try:
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            continue
