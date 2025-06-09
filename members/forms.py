from datetime import date

from django.core.exceptions import ValidationError
from django.forms import DateInput, ModelForm, TextInput
from django.utils.translation import gettext_lazy as _

from .models import Member


class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            'name',
            'phone_number',
            'gender',
            'date_of_birth',
        ]
        labels = {
            'name': _('姓名'),
            'phone_number': _('電話'),
            'gender': _('性別'),
            'date_of_birth': _('生日'),
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
                'required': _('請輸入姓名'),
            },
            'phone_number': {
                'required': _('請輸入電話號碼'),
            },
            'gender': {
                'required': _('請選擇性別'),
                'invalid_choice': _('性別選擇無效'),
            },
            'date_of_birth': {
                'invalid': _('請輸入正確的日期格式'),
            },
        }

    def __init__(self, *args, **kwargs):
        self.is_create = kwargs.pop('is_create', False)
        super().__init__(*args, **kwargs)

        self.fields['name'].required = True
        self.fields['phone_number'].initial = '09'
        self.fields['phone_number'].required = True

        if not self.is_create:
            self.fields['date_of_birth'].widget.attrs['readonly'] = True
            self.fields['date_of_birth'].help_text = _('生日設定完成後，將無法修改。')

    def clean_date_of_birth(self):
        birthday = self.cleaned_data.get('date_of_birth')

        if self.is_create:
            if not birthday:
                raise ValidationError(_('請輸入生日'))
            if birthday > date.today():
                raise ValidationError(_('生日不能是未來的日期'))
            return birthday

        if self.instance and self.instance.pk:
            if self.instance.date_of_birth and birthday != self.instance.date_of_birth:
                raise ValidationError(_('生日不可修改'))

        return birthday
