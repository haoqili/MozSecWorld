from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy as _lazy

# captcha stuff modified from 
# http://www.marcofucci.com/tumblelog/26/jul/2009/integrating-recaptcha-with-django/
from django.conf import settings
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from msw.captcha import submit, displayhtml

class ReCaptchaField(forms.CharField):
    default_error_messages = {
        'captcha_invalid': _(u'Invalid captcha')
    }

    def __init__(self, *args, **kwargs):
        self.widget = ReCaptcha
        self.required = True
        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):
        super(ReCaptchaField, self).clean(values[1])
        recaptcha_challenge_value = smart_unicode(values[0])
        recaptcha_response_value = smart_unicode(values[1])
        check_captcha = submit(recaptcha_challenge_value, 
            recaptcha_response_value, settings.RECAPTCHA_PRIVATE_KEY, {})
        if not check_captcha.is_valid:
            raise forms.util.ValidationError(self.error_messages['captcha_invalid'])
        return values[0]


class ReCaptcha(forms.widgets.Widget):
    recaptcha_challenge_name = 'recaptcha_challenge_field'
    recaptcha_response_name = 'recaptcha_response_field'

    def render(self, name, value, attrs=None):
        return mark_safe(u'%s' % displayhtml(settings.RECAPTCHA_PUBLIC_KEY))

    def value_from_datadict(self, data, files, name):
        return [data.get(self.recaptcha_challenge_name, None), 
            data.get(self.recaptcha_response_name, None)]


class UserCreationCaptchaForm(auth_forms.UserCreationForm):
    recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")

class UserCreationForm(auth_forms.UserCreationForm):
    pass

#-------- end captcha stuff ------------------------------------------------------


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

