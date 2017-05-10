from macrosurl import url

from profileme import views


urlpatterns = (
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^photo-upload/$', views.ProfilePhotoUploadView.as_view(), name='dashboard_photo_upload'),
    url(r'^cv-upload/$', views.ProfileCVUploadView.as_view(), name='dashboard_cv_upload'),
    url(r'^profile-update/$', views.ProfileUpdateView.as_view(), name='dashboard_update_profile'),
    url(r'^company-update/$', views.CompanyUpdateView.as_view(), name='dashboard_update_company'),
    url(r'^invite-users/$', views.InviteCompanyUserView.as_view(), name='dashboard_invite_users'),

    url(r'^company/create/$', views.company_create, name='dashboard_company_create'),
    url(r'^company/pending/$', views.company_pending, name='dashboard_company_pending'),
    url(r'^company/invitation/:uuid/update/$', views.api_company_invitation_request, name='api_company_invitation_request'),
)
