from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from email_validator import EmailNotValidError, validate_email as strict_validate_email

from .models import User


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = '電子郵件'
        self.fields['password1'].label = '密碼'
        self.fields['password2'].label = '確認密碼'
        self.fields['email'].widget.attrs.update({'placeholder': 'example@mail.com'})
        self.fields['email'].error_messages.update(
            {'invalid': '您輸入的電子郵件格式不正確'}
        )
        self.fields['password1'].widget.attrs.update({'placeholder': '請輸入密碼'})
        self.fields['password2'].widget.attrs.update({'placeholder': '再次輸入密碼'})
        self.fields['email'].error_messages['invalid'] = '您輸入的電子郵件格式不正確'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise ValidationError('輸入的密碼不一致')

        if password1 and password1.isdigit():
            raise ValidationError('請使用英文+數字做為你的密碼，這樣會更安全喔')

        if password1 and len(password1) < 8:
            raise ValidationError('密碼太短，請至少輸入 8 個字元')
        return password2

    def clean_email(self):
        raw_email = self.cleaned_data.get('email')
        try:
            # 更嚴格的 email 檢查（格式 + 可達性），並標準化
            valid = strict_validate_email(raw_email, check_deliverability=True)
            email = valid.email  # 自動轉小寫、去空格
        except EmailNotValidError:
            raise ValidationError('請輸入有效的電子郵件地址')
        if User.objects.filter(email=email).exists():
            raise ValidationError('此電子郵件已被註冊，請直接登入或使用其他信箱。')
        return email
