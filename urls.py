from django.conf import settings
from django.conf.urls.defaults import *

from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    (r'^$', redirect_to, {'url': '/msw/'}), # needs last "/" save one redir
    (r'^msw/', include('msw.urls')), # directs to msw/urls.py
    #(r'^', include('msw.urls')), # needs last "/" save one redir

    #(r'^accounts/', include('msw.urls')),
    #(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'apps/msw/templates/msw/demos/login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

## In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
