from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Member
import uuid
from . form import UserForm,MemberForm

# 顯示註冊表單 (GET)
def sign_up(request):
    userform = UserForm()
    memberform = MemberForm()
    return render(request, 'users/sign_up.html',{"userform":userform,"memberform":memberform})

# 處理註冊 (POST)
@require_POST
def create_user(request):
    userform = UserForm(request.POST)
    memberform = MemberForm(request.POST)
    next = request.POST.get("next", reverse("pages:home"))

    if userform.is_valid() and memberform.is_valid():
        user = userform.save(commit=False)
        member = memberform.save(commit=False)
        user.id = uuid.uuid4()
        user.save()
        member.save()
        messages.success(request, "註冊成功！")
        return redirect(next)

    else:
        messages.error(request, "註冊失敗！請檢查輸入的資料。")
        return render(request, "users/sign_up.html", {
            "userform": userform,
            "memberform": memberform,
            "next": next,
        })

# 顯示登入頁面 (GET)
def sign_in(request):
    next = request.GET.get("next", reverse("pages:home"))
    return render(request, "users/sign_in.html", {"next": next})

# 處理登入 (POST)
@require_POST
def create_session(request):
    pass

# 處理登出 (POST)
@require_POST
def delete_session(request):
    pass