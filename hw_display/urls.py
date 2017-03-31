from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', views.homepage, name="home"),
    # auth
    url(r'^render/$', views.vs_login, name="login_user"),
    url(r'^login/$', views.login_render, name='login_form'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'hw_display/logout.html'}, name='logout'),
    # hw
    url(r'^devoirs/', views.show_hw_list, name="hw_list"),
]
