from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^login/', views.auth_login, name='login'),
    url(r'^logout/', views.auth_logout, name='logout'),
    url(r'^register/', views.auth_register, name='register'),
)
