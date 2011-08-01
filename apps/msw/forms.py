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

# File upload
from msw import formfield

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
    #recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")
    pass

class AuthenticationCaptchaForm(auth_forms.AuthenticationForm):
    recaptcha = ReCaptchaField(label="Being a human is awesome! Let me pass!")

######## File Upload stuff #########################
# src: https://github.com/jsocol/kitsune/blob/master/apps/upload/forms.py

MSG_IMAGE_REQUIRED = _lazy(u'You have not selected an image to upload.')
MSG_IMAGE_LONG = _lazy(
    u'Please keep the length of your image filename to %(max)s '
     'characters or less. It is currently %(length)s characters.')
MSG_IMAGE_EXTENSION = _lazy(u'Please upload an image with one of the '
                            u'following extensions: jpg, jpeg, png, gif.')
ALLOWED_IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif')


class ImageAttachmentUploadForm(forms.Form):
    """Image upload form with image file checks"""
    # forms.ImageField requires PIL
    image = formfield.ImageProcessField(error_messages={'required': MSG_IMAGE_REQUIRED,
                                         'max_length': MSG_IMAGE_LONG},
                                          max_length=settings.MAX_FILENAME_LENGTH)
    def clean(self):
        c = super(ImageAttachmentUploadForm, self).clean()
        clean_image_extension(c.get('image'))
        return c


def clean_image_extension(form_field):
    """Ensure only images of certain extensions can be uploaded."""
    if form_field:
        if '.' not in form_field.name:
            raise ValidationError(MSG_IMAGE_EXTENSION)
        _, ext = form_field.name.rsplit('.', 1)
        if ext.lower() not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(MSG_IMAGE_EXTENSION)
