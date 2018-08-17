from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views


admin.autodiscover()


urlpatterns = [
    url("^mmh-admin/", include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls'), name='login'),
    url(r'^scribbler/', include('scribbler.urls')),
    url(r'', include('myhpom.urls', namespace='myhpom')),
]

# These should be served by nginx for deployed environments,
# presumably this is here to allow for running without DEBUG
# on in local dev environments.
if not settings.DEBUG:   # if DEBUG is True it will be served automatically
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
