import debug_toolbar

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from django_js_reverse.views import urls_js

from profileme.views import InviteCompanyUserView


urlpatterns = [
    url(r'^', include('recruit.urls')),
    url(r'^jsreverse/$', urls_js, name='js_reverse'),
#    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
#    url(r'^', include('simplepages.urls', namespace='simplepages')),
    url(r'^dashboard/', include('profileme.urls')),
    url(r'^company-invitation/(?P<invite_key>[0-9A-Za-z]+)$', InviteCompanyUserView.as_view(), name='accept-company-invitation'),
    url(r'^dashboard/', include('profileme.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^recadmin/', include(admin.site.urls)),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
