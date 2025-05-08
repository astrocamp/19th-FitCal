from django.contrib.auth.forms import UserCreationForm

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
        self.fields['password1'].widget.attrs.update({'placeholder': '請輸入密碼'})
        self.fields['password2'].widget.attrs.update({'placeholder': '再次輸入密碼'})
