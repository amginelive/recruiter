
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin

import debug_toolbar
from django_js_reverse.views import urls_js
from macrosurl import url


urlpatterns = [
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^recadmin/', include(admin.site.urls)),

    url(r'^', include('recruit.urls', namespace='recruit')),
    url(r'^companies/', include('companies.urls', namespace='companies')),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^chat/', include('chat.urls', namespace='chat')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
