from datetime import date

from django.core.exceptions import ValidationError
from django.forms import DateInput, ModelForm, TextInput

from .models import Member


class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            'name',
            'phone_number',
            'gender',
            'date_of_birth',
            'line_id',
            'google_id',
        ]
        labels = {
            'name': '姓名',
            'phone_number': '電話',
            'gender': '性別',
            'date_of_birth': '生日',
            'line_id': 'LINE ID',
            'google_id': 'Google ID',
        }
        widgets = {
            'phone_number': TextInput(attrs={'type': 'tel'}),
            'date_of_birth': DateInput(
                attrs={
                    'type': 'date',
                    'max': date.today().isoformat(),
                }
            ),
        }
        error_messages = {
            'name': {
                'required': '請輸入姓名',
            },
            'phone_number': {
                'required': '請輸入電話號碼',
            },
            'gender': {
                'required': '請選擇性別',
                'invalid_choice': '性別選擇無效',
            },
            'date_of_birth': {
                'required': '請輸入生日',
                'invalid': '請輸入正確的日期格式',
            },
        }

    def __init__(self, *args, **kwargs):
        self.is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['phone_number'].initial = '09'
        self.fields['phone_number'].required = True
        self.fields['gender'].required = True
        self.fields['date_of_birth'].required = True

        self.fields['line_id'].required = False
        self.fields['google_id'].required = False

        if not self.is_create:
            self.fields['date_of_birth'].widget.attrs['readonly'] = True
            self.fields['date_of_birth'].help_text = '此欄位僅供查看，無法修改。'

    def clean_date_of_birth(self):
        birthday = self.cleaned_data.get('date_of_birth')

        if self.is_create:
            if not birthday:
                raise ValidationError('請輸入生日')
            if birthday > date.today():
                raise ValidationError('生日不能是未來的日期')
            return birthday

        if self.instance and self.instance.pk:
            if self.instance.date_of_birth and birthday != self.instance.date_of_birth:
                raise ValidationError('生日不可修改')

        return birthday
