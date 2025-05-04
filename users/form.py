from django import forms
from django.contrib.auth.models import User
from .models import Member

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密碼")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        labels = {
            'username': '帳號',
            'email': '電子郵件',
            'password': '密碼',
        }

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'phone_number', 'gender', 'date_of_birth']
        labels = {
            'name': '姓名',
            'phone_number': '電話號碼',
            'gender': '性別',
            'date_of_birth': '出生日期',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'name': '請輸入您的姓名',
            'phone_number': '請輸入您的電話號碼',}