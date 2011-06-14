import urllib
import bleach
from django.db import models
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from django.conf import settings

# Django automatically creates a table for each "class" here, named "[app name]_[class name]"
# so the table of "class Page" is "msw_page"
# each attribute of a class corresponds to a column in its table
class Page(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)
    description = models.TextField()
    prevention = models.TextField()
    demo = models.CharField(max_length=2000)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

class RichText(models.Model):
    name = models.CharField(max_length=200)
    comment = models.TextField()

    def __unicode__(self):
        return self.name + ": " + self.comment


# returns True if url is checked to be non-malicious, else False
# the 1 url's format must be "http://..."
def urlCheck(url):
    data = "1\n" + url
    if settings.GOOGLE_SAFEBROWSING_LOOKUP:
        # Google SafeBrowsing Lookup: http://code.google.com/apis/safebrowsing/lookup_guide.html#AQuickExamplePOSTMethod
        f = urllib.urlopen(settings.GSB_URL + "?client=api&apikey=" + settings.GSB_API_KEY + "&appver=1.5.2&pver=3.0", data)
        response_code = f.code
        # print f.read() # prints out the response (for multiple URLS)
        # for more info: http://code.google.com/apis/safebrowsing/lookup_guide.html#HTTPPOSTRequestResponseBody
        if response_code == 204:
            return True 
    return False

# ModelForm https://docs.djangoproject.com/en/dev/topics/forms/modelforms/
class RichTextForm(ModelForm):
    class Meta:
        model = RichText
    
    def clean_name(self):
        data = self.cleaned_data['name']
        #is it an URL?...does it have "http"
        # ASSUMING the ENTIRE NAME FIELD is a URL that starts with http://...
        if "http" in data:
            if urlCheck(data):
                data = data
                # adds href to data
                data = bleach.linkify(data)
            else:
                data = data+"DANGEROUS LINK!!!!!!!"
        return bleach.clean(data)

    def clean_comment(self): #comment must match one of the fields of model
        data = self.cleaned_data['comment']
        return bleach.clean(data)
