from django.conf.urls import url

from profileme import views

urlpatterns = (
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^photo-upload/$', views.ProfilePhotoUploadView.as_view(), name='dashboard_photo_upload'),
    url(r'^cv-upload/$', views.ProfileCVUploadView.as_view(), name='dashboard_cv_upload'),
    url(r'^profile-update/$', views.ProfileUpdateView.as_view(), name='dashboard_update_profile'),
    url(r'^company-update/$', views.CompanyUpdateView.as_view(), name='dashboard_update_company'),
    url(r'^invite-users/$', views.InviteCompanyUserView.as_view(), name='dashboard_invite_users'),
)
