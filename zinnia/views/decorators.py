"""Decorators for zinnia.views"""
from functools import wraps

from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import login
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache


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
    return TemplateResponse(request, 'zinnia/password.html', {'error': error})


def protect_entry(view):
    """Decorator performing a security check if needed
    around the generic.date_based.entry_detail view
    and specify the template used to render the entry"""

    @wraps(view)
    def wrapper(*args, **kwargs):
        """Do security check and retrieve the template"""
        request = args[0]
        entry = get_object_or_404(kwargs['queryset'], slug=kwargs['slug'],
                                  creation_date__year=kwargs['year'],
                                  creation_date__month=kwargs['month'],
                                  creation_date__day=kwargs['day'])

        if entry.login_required and not request.user.is_authenticated():
            return login(request, 'zinnia/login.html')
        if entry.password and entry.password != \
               request.session.get('zinnia_entry_%s_password' % entry.pk):
            return password(request, entry)
        kwargs['template_name'] = entry.template
        return view(*args, **kwargs)

    return wrapper
