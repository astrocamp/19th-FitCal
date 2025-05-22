from django.contrib import messages
from django.shortcuts import redirect


class BlockMerchantCartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 如果登入不是會員就攔截 /carts/ 或以 /carts/ 開頭的 URL
        if request.path.startswith('/carts/'):
            if not (request.user.is_authenticated and request.user.is_member):
                messages.error(request, '您沒有購物車功能。')
                return redirect('users:index')
        return self.get_response(request)
