from macrosurl import url

from . import (
    api,
    views,
)

urlpatterns = (
    url(r'^profile/update/$', views.profile_update, name='profile_update'),
    url(r'^profile/:slug/$', views.candidate_profile, name='candidate_profile'),
    url(r'^candidate/search/$', views.candidate_search, name='candidate_search'),
    url(r'^agent/search/$', views.agent_search, name='agent_search'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^settings/update/$', views.settings_update, name='settings_update'),

    url(r'^photo/upload/api/$', api.profile_photo_upload, name='profile_photo_upload'),
    url(r'^cv/upload/api/$', api.profile_cv_upload, name='profile_cv_upload'),
    url(r'^profile/details/:pk/update/api/$', api.candidate_profile_detail_update, name='candidate_profile_detail_update'),
    url(r'^user-note/create/api/$', api.user_note_create, name='user_note_create'),
    url(r'^user-note/:pk/update/api/$', api.user_note_update, name='user_note_update'),
    url(r'^user-note/:pk/delete/api/$', api.user_note_delete, name='user_note_delete'),
    url(r'^tracking/:pk/api/$', api.tracking, name='tracking'),
)
