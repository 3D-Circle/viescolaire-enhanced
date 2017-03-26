from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup


LOGIN_URL = "https://viescolaire.ecolejeanninemanuel.net/auth.php"


class ViescolaireAuth:
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """
    def authenticate(self, template_name=None, username=None, password=None, **kwargs):
        playload = {'login': username, 'mdp': password}
        user_session = requests.Session()
        r = user_session.post(LOGIN_URL, data=playload)
        response = BeautifulSoup(r.content, "html.parser")
        login_success = "Erreur - Le mot de passe est incorrecte. Veuillez réessayer." not in response
        print("AUTH")
        if login_success:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
