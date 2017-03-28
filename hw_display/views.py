from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .vs_helper_functions import Homework, InvalidCredentials
from django.http import HttpResponseRedirect


LOGIN_URL = "https://viescolaire.ecolejeanninemanuel.net/auth.php"


def homepage(request):
    """render the homepage"""
    if request.user.is_authenticated() and hasattr(request.session, 'username'):
        playload = {'login': request.session.username, 'mdp': request.session.password}
        try:
            hw = Homework(playload)  # checking validity of password
        except InvalidCredentials:
            return login_render(request, invalid=True)
        else:
            hw_dict = hw.get_all()
            return render(request, "hw_display/homepage.html", {"hw_dict": hw_dict})
    else:
        return redirect('loginform')


def vs_login(request):
    username = request.POST['username'].lower()  # lowercase email is still the same
    password = request.POST['password']
    playload = {'login': username, 'mdp': password}
    try:
        hw = Homework(playload)
    except InvalidCredentials:
        return login_render(request, invalid=True)
    user = authenticate(username=username, password=password)
    if user is None:
        # first time user
        user = User.objects.create_user(username=username, password=password)
    # login(request, user)
    # storing credentials to be accessed later
    request.session.username = username
    request.session.password = password
    return redirect("home", permanent=True)


def login_render(request, invalid=False):
    return render(request, "hw_display/login.html", {'invalid': invalid})
