from django.conf.urls import url
from . import views
from django.contrib.auth.views import auth_login
from django.contrib.auth import views as auth_views
from .forms import VsAuthForm


urlpatterns = [
    url("^$", views.homepage, name="home"),
    url("^render/$", views.my_view, name="loginuser"),
    url(r'^login/$', views.login_render, name='loginform'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]