from django.forms import ModelForm

from .models import Store


class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = ['address', 'phone_number', 'tax_id']

        labels = {
            'address': '地址',
            'phone_number': '聯絡電話',
            'tax_id': '統編',
        }
