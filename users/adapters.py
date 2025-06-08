import logging

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)  # 將 LINE 登入綁定到此使用者
            except User.DoesNotExist:
                pass  # 如果不存在就照預設邏輯走

    def is_auto_signup_allowed(self, request, sociallogin):
        print('LINE 回傳資料：', sociallogin.account.extra_data)
        return True  # 暫時允許 auto signup 觀察是否有 email

    def is_open_for_signup(self, request, sociallogin):
        # 允許自動註冊，跳過 signup 頁
        return True

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        if not user.username:
            user.username = (
                extra_data.get('email') or user.email or sociallogin.account.uid
            )

        if not user.email:
            user.email = extra_data.get('email', '')

        if not user.first_name:
            user.first_name = extra_data.get('name') or extra_data.get(
                'displayName', ''
            )

        user.save()
        sociallogin.save(request)
        return user
