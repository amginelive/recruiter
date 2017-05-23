from macrosurl import url

from . import views

urlpatterns = (
    url(r'^profile/update/$', views.profile_update, name='profile_update'),
    url(r'^profile/:slug/$', views.profile_detail, name='profile_detail'),
    url(r'^photo/upload/$', views.profile_photo_upload, name='profile_photo_upload'),
    url(r'^cv/upload/$', views.profile_cv_upload, name='profile_cv_upload'),
)
