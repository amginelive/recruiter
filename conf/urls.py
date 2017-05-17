
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin

import debug_toolbar
from django_js_reverse.views import urls_js
from macrosurl import url

from profileme.views import InviteCompanyUserView


urlpatterns = [
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^', include('recruit.urls', namespace='recruit')),
    url(r'^dashboard/', include('profileme.urls')),
    url(r'^recadmin/', include(admin.site.urls)),
    url(r'^company-invitation/(?P<invite_key>[0-9A-Za-z]+)$', InviteCompanyUserView.as_view(), name='accept-company-invitation'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
