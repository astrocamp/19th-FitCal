from django.forms import DateInput, ModelForm

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
            'phone_number': DateInput(attrs={'type': 'tel'}),
            'date_of_birth': DateInput(attrs={'type': 'date'}),
        }
