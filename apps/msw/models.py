import bleach
from django.db import models
from django.forms import ModelForm
from django.template.defaultfilters import slugify

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

# ModelForm https://docs.djangoproject.com/en/dev/topics/forms/modelforms/
class RichTextForm(ModelForm):
    class Meta:
        model = RichText
    '''
    name = forms.CharField(max_length=200)
    comment = forms.TextField()

    def __unicode__(self):
        return self.name + ": " + self.comment
    '''

    def clean_comment(self): #comment must match one of the fields of model
        data = self.cleaned_data['comment']
        return bleach.clean(data)
