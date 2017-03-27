from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

LOGIN_URL = "https://viescolaire.ecolejeanninemanuel.net/auth.php"


def homepage(request):
    """render the homepage"""
    if request.user.is_authenticated():
        return render(request, "hw_display/homepage.html")
    else:
        return redirect('loginform')


def vs_login(request):
    username = request.POST['username']
    password = request.POST['password']
    playload = {'login': username, 'mdp': password}
    user_session = requests.Session()
    r = user_session.post(LOGIN_URL, data=playload)
    response = BeautifulSoup(r.content, "html.parser")
    login_success = "Erreur" not in response.text
    print(login_success)
    print(response.text)
    if login_success:
        user = authenticate(username=username, password=password)
        if user is None:
            user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("home")
    else:
        return redirect("loginform")


def login_render(request):
    return render(request, "hw_display/login.html")