"""Protection mixins for Zinnia views"""
from django.contrib.auth.views import LoginView


class LoginMixin(object):
    """
    Mixin implemeting a login view
    configurated for Zinnia.
    """

    def login(self):
        """
        Return the login view.
        """
        return LoginView.as_view(
            template_name='zinnia/login.html'
        )(self.request)


class PasswordMixin(object):
    """
    Mixin implementing a password view
    configurated for Zinnia.
    """
    error = False

    def password(self):
        """
        Return the password view.
        """
        return self.response_class(request=self.request,
                                   template='zinnia/password.html',
                                   context={'error': self.error})


class EntryProtectionMixin(LoginMixin, PasswordMixin):
    """
    Mixin returning a login view if the current
    entry need authentication and password view
    if the entry is protected by a password.
    """
    session_key = 'zinnia_entry_%s_password'

    def get(self, request, *args, **kwargs):
        """
        Do the login and password protection.
        """
        response = super(EntryProtectionMixin, self).get(
            request, *args, **kwargs)
        if self.object.login_required and not request.user.is_authenticated:
            return self.login()
        if (self.object.password and self.object.password !=
                self.request.session.get(self.session_key % self.object.pk)):
            return self.password()
        return response

    def post(self, request, *args, **kwargs):
        """
        Do the login and password protection.
        """
        self.object = self.get_object()
        self.login()
        if self.object.password:
            entry_password = self.request.POST.get('entry_password')
            if entry_password:
                if entry_password == self.object.password:
                    self.request.session[self.session_key %
                                         self.object.pk] = self.object.password
                    return self.get(request, *args, **kwargs)
                else:
                    self.error = True
            return self.password()
        return self.get(request, *args, **kwargs)
