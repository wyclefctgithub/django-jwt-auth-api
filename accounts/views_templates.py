from django.shortcuts import render

def register_page(request):
    return render(request, "accounts/register.html")

def login_page(request):
    return render(request, "accounts/login.html")

def forgot_password_page(request):
    return render(request, "accounts/forgot_password.html")

def reset_password_page(request, uid, token):
    return render(request, "accounts/reset_password.html")

def profile_page(request):
    return render(request, "accounts/profile.html")
