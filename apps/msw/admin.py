from msw.models import Page, RichText, MembersPostUser, MembersPostText
from django.contrib import admin

# could add more complicated stuff here consult:
#    tutorial: https://docs.djangoproject.com/en/dev/intro/tutorial02/#enter-the-admin-site
#    tutorial finished admin.py: https://github.com/haoqili/Django-Tutorial-Directory/blob/master/tutorialSite/polls/admin.py

admin.site.register(Page)
admin.site.register(RichText)
admin.site.register(MembersPostUser)
admin.site.register(MembersPostText)
