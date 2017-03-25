from django.shortcuts import render


def homepage(request):
    """render the homepage"""
    return render(request, "hw_display/login.html")
