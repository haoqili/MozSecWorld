from django.conf import settings
from django.conf.urls.defaults import *

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
    (r'^(?P<input_slug>\w+)/demo/$', 'demo'), 

    (r'^cookie$', 'cookie'), # test cookie settings # TO-DELETE??
    (r'^richtext$', 'richtext'), # test cookie settings

    # N.B.: didn't make '^.*/demo/(?P<slug>\w+)$' because each page has different httpresponse settings, i.e. each page has to have its own function in views.py
    # x-frame-options
    (r'^x_frame_options/demo/xfo_deny$', 'xfo_deny'), 
    (r'^x_frame_options/demo/xfo_sameorigin$', 'xfo_sameorigin'), 
    (r'^x_frame_options/demo/xfo_allow$', 'xfo_allow'), 

    # http-only stuff
    (r'^set_cookie_httponly/demo/httponly_true$', 'httponly_true'), # HTTPOnly demo


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
