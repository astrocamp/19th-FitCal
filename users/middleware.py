from django.shortcuts import redirect
from django.urls import reverse


class RoleGuardMiddleware:
    """
    限制會員與店家使用者只能進入對應角色的頁面：
    - member 登入者不能訪問 /stores/
    - store 登入者不能訪問 /members/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # For測試，未登入或超級使用者不做限制
        if not user.is_authenticated or user.is_superuser:
            return self.get_response(request)

        path = request.path

        # 若是會員但訪問店家頁面，導回會員主頁
        if hasattr(user, 'member') and '/stores/' in path:
            return redirect(reverse('members:show', args=[user.member.id]))

        # 若是店家但訪問會員頁面，導回店家主頁
        if hasattr(user, 'store') and '/members/' in path:
            return redirect(reverse('stores:show', args=[user.store.id]))

        return self.get_response(request)
