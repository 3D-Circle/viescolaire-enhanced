from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .vs_helper_functions import Homework, InvalidCredentials


LOGIN_URL = "https://viescolaire.ecolejeanninemanuel.net/auth.php"


def homepage(request):
    """redirect to correct page (if user is logged in or not)"""
    if request.user.is_authenticated() and hasattr(request.session, 'username'):
        return redirect("/devoirs/")
    else:
        return redirect("/login/")


def vs_login(request):
    username = request.POST['username'].lower()  # lowercase email is still the same
    password = request.POST['password']
    payload = {'login': username, 'mdp': password}
    try:
        Homework(payload)
    except InvalidCredentials:
        return login_render(request, invalid=True)
    user = authenticate(username=username, password=password)
    if user is None:
        # first time user
        user = User.objects.create_user(username=username, password=password)
    login(request, user)
    # storing credentials to be accessed later
    request.session['username'] = username
    request.session['password'] = password
    return redirect("hw_list")


def login_render(request, invalid=False, unauthorized=False):
    return render(request, "hw_display/login.html", {'invalid': invalid, 'unauthorized': unauthorized})


def show_hw_list(request):
    username = request.session.get('username')
    password = request.session.get('password')
    if request.user.is_authenticated() and username and password:
        payload = {'login': username, 'mdp': password}
        try:
            hw = Homework(payload)  # checking validity of password
        except InvalidCredentials:
            return redirect("login_form", invalid=True)
        else:
            hw_dict = [i[1] for i in hw.get_all()]
            return render(request, "hw_display/hw_list.html", {"hw_dict": hw_dict})
    else:
        return redirect('login_form')


def get_hw_by_id(request, _id):
    username = request.session.get('username')
    password = request.session.get('password')
    if username and password:
        obj = Homework(payload={'login': username, 'mdp': password})
        hw = obj.get_hw_by_id(_id)
        return render(request, 'hw_display/individual_hw.html', {'hw_details': hw})
    else:
        return redirect('login_form', unauthorized=True)
