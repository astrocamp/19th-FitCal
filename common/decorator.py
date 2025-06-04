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
            return redirect_with_message(
                req, 'users:index', '您不是會員，無法訪問此頁面'
            )

        # 從 kwargs 獲取 'id'
        member_id_from_url = kwargs.get('member_id') or kwargs.get('id')

        if member_id_from_url is None or str(getattr(req.user.member, 'id', '')) == str(
            member_id_from_url
        ):
            return view_func(req, *args, **kwargs)
        else:
            return redirect_with_message(
                req, 'users:index', '你沒有權限存取其他會員後台的權限'
            )

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
            return redirect_with_message(
                req, 'users:index', '您不是會員，無法訪問此頁面'
            )

        # return view_func(req, *args, **kwargs)

        store_id = kwargs.get('store_id') or kwargs.get(
            'id'
        )  # 或 store_id，視你的 urls.py 而定

        if store_id is not None and str(getattr(req.user.store, 'id', '')) == str(
            store_id
        ):
            return view_func(req, *args, **kwargs)
        else:
            return redirect_with_message(
                req, 'stores:index', '你沒有權限存取這個商家後台'
            )

    return _wrapped_view
