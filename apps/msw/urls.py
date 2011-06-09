from django.conf import settings
from django.conf.urls.defaults import *
from msw.models import Page

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('msw.views', # gets information from views.py

    (r'^$', 'index'), # goes to views.py's "def index"

    #####
    ## Named groups, read more here: https://docs.djangoproject.com/en/1.3/topics/http/urls/#named-groups
    ## (?P<argument_name>regex) saves whatever matches in regex to argument_name
    ## to be put as an argument into the corresponding views.py's def.
    #####
    (r'^(?P<input_slug>\w+)/$', 'detail'), # goes to views.py's "def detail" with input_slug as an argument.

    #(r'^(?P<msw_id>\w+)/demo/$', 'demo'), # to be implemented in the future



    #### --- stuff they had before ----

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
