from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def store_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_store:
            messages.error(req, '您不是店家，無法訪問此頁面')
            return redirect('users:index')
        return view_func(req, *args, **kwargs)

    return _wrapped_view


def member_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_member:
            messages.error(req, '您不是會員，無法訪問此頁面')
            return redirect('users:index')
        return view_func(req, *args, **kwargs)

    return _wrapped_view
