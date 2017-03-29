from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.homepage, name="home"),
    url(r'^render/$', views.vs_login, name="loginuser"),
    url(r'^login/$', views.login_render, name='loginform'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]