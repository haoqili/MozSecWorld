from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_lazy as _lazy

# captcha stuff read:
# http://curioushq.blogspot.com/2011/07/recaptcha-on-django.html
from django.conf import settings
from django import forms
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from msw.captcha import submit, displayhtml

# Blacklisted Password
from .models import BlacklistedPassword

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


class UserCreationForm(auth_forms.UserCreationForm):
    pass

    # overrides src/django/django/contrib/auth/forms.py's method
    def clean_password2(self):
        # check that password not in blacklist
        pw = self.cleaned_data['password1']
        if BlacklistedPassword.blocked(pw):
            raise forms.ValidationError(_('Please pick a less commonly used password.'))
        # super to check that passwords agree
        return super(UserCreationForm, self).clean_password2()

class UserCreationCaptchaForm(auth_forms.UserCreationForm):
    recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")

    # overrides src/django/django/contrib/auth/forms.py's method
    def clean_password2(self):
        # check that password not in blacklist
        pw = self.cleaned_data['password1']
        if BlacklistedPassword.blocked(pw):
            raise forms.ValidationError(_('Please pick a less commonly used password.'))
        # super to check that passwords agree
        return super(UserCreationCaptchaForm, self).clean_password2()

#-------- end captcha stuff ------------------------------------------------------


class AuthenticationForm(auth_forms.AuthenticationForm):
    #TODO: delete recaptcha from this form once recaptcha works
    recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")

class AuthenticationCaptchaForm(auth_forms.AuthenticationForm):
    recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")
    def __init__(self, *args, **kwargs):
        super(AuthenticationCaptchaForm, self).__init__(*args, **kwargs)

        if self.fields.get('recaptcha'):
            del self.fields['recaptcha']
