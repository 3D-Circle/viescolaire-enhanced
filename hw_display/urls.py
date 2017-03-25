from django.conf.urls import url
from django.contrib.auth.views import auth_login
from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^login/$', auth_login, {'template_name': 'hw_display/login.html'}),
]