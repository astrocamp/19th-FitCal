import logging

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        若該 email 已存在於系統，則將這個 social account 綁定到該使用者。
        不進行寫入 EmailAddress，避免 user 尚未儲存時寫入失敗。
        """
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                if not sociallogin.is_existing:
                    sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass

    def is_auto_signup_allowed(self, request, sociallogin):
        print('LINE 回傳資料：', sociallogin.account.extra_data)
        return True

    def is_open_for_signup(self, request, sociallogin):
        return True

    def save_user(self, request, sociallogin, form=None):
        """
        將社群登入的使用者資訊儲存至本地帳號，並確保有 email、username 等必要欄位。
        此處也建立 EmailAddress 紀錄並設定角色。
        """
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        # 設定帳號基本資訊
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

        # 👉 自動加上 member 角色
        if not user.role:
            user.role = 'member'

        user.save()
        sociallogin.save(request)

        # 設定已驗證 email
        if user.email:
            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={'verified': True, 'primary': True},
            )

        return user
