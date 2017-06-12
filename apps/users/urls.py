from macrosurl import url

from . import (
    api,
    views,
)

urlpatterns = (
    url(r'^profile/update/$', views.profile_update, name='profile_update'),
    url(r'^profile/:slug/$', views.profile_detail, name='profile_detail'),
    url(r'^candidate/search/$', views.candidate_search, name='candidate_search'),
    url(r'^agent/search/$', views.agent_search, name='agent_search'),

    url(r'^photo/upload/api/$', api.profile_photo_upload, name='profile_photo_upload'),
    url(r'^cv/upload/api/$', api.profile_cv_upload, name='profile_cv_upload'),
    url(r'^profile/:pk/update/api/$', api.profile_candidate_update, name='profile_candidate_update'),
)
