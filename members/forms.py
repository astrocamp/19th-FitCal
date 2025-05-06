from django.forms import DateInput, ModelForm, TextInput

from .models import Member


class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['phone_number', 'gender', 'date_of_birth', 'line_id', 'google_id']
        labels = {
            'phone_number': '電話',
            'gender': '性別',
            'date_of_birth': '生日',
            'line_id': 'LINE ID',
            'google_id': 'Google ID',
        }
        widgets = {
            'phone_number': TextInput(attrs={'type': 'tel'}),
            'date_of_birth': DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
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
        super().__init__(*args, **kwargs)

        self.fields['phone_number'].initial = '09'
        self.fields['phone_number'].required = True
        self.fields['gender'].required = True
        self.fields['date_of_birth'].required = True

        self.fields['line_id'].required = False
        self.fields['google_id'].required = False
