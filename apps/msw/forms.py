from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy as _lazy
from django.utils.http import int_to_base36


class UserCreationForm(auth_forms.UserCreationForm):
    #email = forms.EmailField(required=False)
    pass


class AuthenticationForm(auth_forms.AuthenticationForm):
    # /src/django/django/contrib/auth/forms.py
    #email = forms.EmailField()
    
    # from jsocol's kitsune
    """Overrides the default django form.

    * Doesn't prefill password on validation error.
    * Allows logging in inactive users (initialize with `only_active=False`).
    """
    password = forms.CharField(label=_lazy(u"Password"),
                               widget=forms.PasswordInput(render_value=False))

    def __init__(self, request=None, only_active=True, *args, **kwargs):
        self.only_active = only_active
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)

# Decorators: https://docs.djangoproject.com/en/dev/topics/auth/#the-login-required-decorator
#@login_required
#def members_page(request):
#    return HttpResponse("You're a member!")

