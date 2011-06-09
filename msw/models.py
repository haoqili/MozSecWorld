from django.db import models

# Django automatically creates a table for each "class" here, named "[app name]_[class name]"
# so the table of "class Page" is "msw_page"
# each attribute of a class corresponds to a column in its table
class Page(models.Model):
    urlname = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)
    description = models.CharField(max_length=5000)
    prevention = models.CharField(max_length=5000)
    demo = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.title
