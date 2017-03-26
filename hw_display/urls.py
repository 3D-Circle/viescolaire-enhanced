from django.conf.urls import url
from django.contrib.auth.views import auth_login
from . import views, user_handling
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(
        r'^login/$',
        user_handling.ViescolaireAuth.authenticate,
        {'template_name': 'hw_display/login.html'},
        name='login'
    ),
    url(r'^logout/$', auth_views.logout, name='logout'),
]