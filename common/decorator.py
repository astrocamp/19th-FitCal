from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


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
        if not req.user.is_member:
            return redirect_with_message(
                req, 'users:index', _('您不是會員，無法訪問此頁面')
            )
        try:
            _ = req.user.member
        except Exception:
            return redirect_with_message(req, 'members:new', _('請先補充會員資料'))

        member_id_from_url = kwargs.get('member_id')

        if member_id_from_url is not None and str(
            getattr(req.user.member, 'id', '')
        ) != str(member_id_from_url):
            return redirect_with_message(
                req, 'users:index', _('你沒有權限存取其他會員後台的權限')
            )
        return view_func(req, *args, **kwargs)

    return _wrapped_view


def store_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped_view(req, *args, **kwargs):
        if not req.user.is_store:
            return redirect_with_message(
                req, 'users:index', _('您不是店家，無法訪問此頁面')
            )
        try:
            _ = req.user.store
        except Exception:
            return redirect_with_message(req, 'stores:new', _('請先補充店家資料'))

        store_id_from_url = kwargs.get('store_id')

        if store_id_from_url is not None and str(
            getattr(req.user.store, 'id', '')
        ) != str(store_id_from_url):
            return redirect_with_message(
                req, 'stores:index', _('你沒有權限存取這個店家後台')
            )
        return view_func(req, *args, **kwargs)

    return _wrapped_view
