from django.conf.urls import url

from recruit import views

urlpatterns = (
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^search$', views.SearchView.as_view(), name='search'),
)
