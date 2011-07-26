from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import login as auth_login_view

from . import views

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('msw.views', # gets information from views.py

    url(r'^$', views.index, name="mswindex"), # goes to views.py's "def index"


    #####
    ## Named groups, read more here: https://docs.djangoproject.com/en/1.3/topics/http/urls/#named-groups
    ## (?P<argument_name>regex) saves whatever matches in regex to argument_name
    ## to be put as an argument into the corresponding views.py's def.
    #####
    url(r'^(?P<input_slug>\w+)/$', views.detail, name='detail'), # goes to views.py's "def detail" with input_slug as an argument.
    (r'^(?P<input_slug>\w+)/demo/$', 'demo'), 

    # N.B.: didn't make '^.*/demo/(?P<slug>\w+)$' because each page has different httpresponse settings, i.e. each page has to have its own function in views.py
    # x-frame-options
    (r'^x_frame_options/demo/xfo_deny$', 'xfo_deny'), 
    (r'^x_frame_options/demo/xfo_sameorigin$', 'xfo_sameorigin'), 
    (r'^x_frame_options/demo/xfo_allow$', 'xfo_allow'), 

    # sql
    (r'^parameterized_sql/demo/sql_ajax_server$', 'sql_ajax_server'),

    #### Login / Authentication
    url(r'^good_auth/demo/login', views.login, name='login'),
    url(r'^good_auth/demo/register', 'register'),
    url(r'^good_auth/demo/logout', 'logout'),
    url(r'^good_auth/demo/membersOnly', 'membersOnly', name='membersOnly'),
    
    #### Access Control
    url(r'^accesscontrol/demo/membersPost', 'membersPost'),
    url(r'^accesscontrol/demo/ac_ajax_server', 'ac_ajax_server', name='ac_ajax_server'),

    #### File upload
    url(r'^fileupload/demo/recent_imgs', 'recent_imgs', name='recent_imgs'),

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
