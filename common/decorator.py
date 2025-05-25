from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse


def redirect_with_message(req, url_name, msg):
    messages.error(req, msg)
    url = reverse(url_name)
    if req.headers.get('HX-Request') == 'true':
        # 給 HTMX 的轉址處理
        response = JsonResponse({})
        response['HX-Redirect'] = url
        return response
    else:
        return redirect(url)


def member_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if req.user.is_member:
            try:
                _ = req.user.member
            except Exception:
                return redirect_with_message(req, 'members:new', '請先補充會員資料')
        else:
            return redirect_with_message('users:index', '您不是會員，無法訪問此頁面')

        return view_func(req, *args, **kwargs)

    return _wrapped_view


def store_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if req.user.is_store:
            try:
                _ = req.user.store
            except Exception:
                return redirect_with_message(req, 'stores:new', '請先補充會員資料')
        else:
            return redirect_with_message('users:index', '您不是會員，無法訪問此頁面')

        return view_func(req, *args, **kwargs)

    return _wrapped_view
