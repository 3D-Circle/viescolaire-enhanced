from django import forms
from django.contrib.auth.forms import AuthenticationForm


class VsAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        print("USER:")
        print(vars(user))