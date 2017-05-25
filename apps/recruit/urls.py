from macrosurl import url

from . import (
    api,
    views,
)


urlpatterns = (
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^job/posts/$', views.job_post_list, name='job_post_list'),
    url(r'^job/posts/:uuid/$', views.job_post_detail, name='job_post_detail'),
    url(r'^job/posts/create/$', views.job_post_create, name='job_post_create'),
    url(r'^job/posts/:uuid/update/$', views.job_post_update, name='job_post_update'),
    url(r'^job/posts/:uuid/delete/$', views.job_post_delete, name='job_post_delete'),

    url(r'^connection/request/$', api.connection_request_create, name='connection_request_create'),
)
