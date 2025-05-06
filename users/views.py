from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from . form import UserForm
from django.contrib.auth import authenticate

# 顯示註冊表單 (GET)
def sign_up(request):
    userform = UserForm()
    return render(request, 'users/sign_up.html',{"userform":userform})

# 處理註冊 (POST)
@require_POST
def create_user(request):
    userform = UserForm(request.POST)
    if userform.is_valid():
        user=userform.save()
        login(request, user)
        return redirect("pages:home")
    else:
        return render(request, "users/sign_up.html", {"userform": userform, })

# 顯示登入頁面 (GET)
def sign_in(request):
    return render(request, "users/sign_in.html")

# 處理登入 (POST)
@require_POST
def create_session(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(
        email=email,
        password=password,
    )
    if user is not None:
        login(request, user)
        return redirect("pages:home")
    else:
        return redirect("users:sign_in")


# 處理登出 (POST)
@require_POST
def delete_session(request):
    logout(request)
    return redirect("pages:home")