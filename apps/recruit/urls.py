from django.conf.urls import url

from recruit import views

urlpatterns = (
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^job/posts/$', views.job_post_list, name='job_post_list'),
)
