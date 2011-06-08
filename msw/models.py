from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)
    description = models.CharField(max_length=5000)
    prevention = models.CharField(max_length=5000)
    demo = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.title
