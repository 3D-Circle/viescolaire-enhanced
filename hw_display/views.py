from django.shortcuts import render
from . import user_handling


def homepage(request):
    """render the homepage"""
    return render(request, "hw_display/login.html")
