from django.forms import ModelForm

from .models import Store


class StoreForm(ModelForm):
    class Meta:
        model = Store
        fields = [
            'name',
            'address',
            'phone_number',
            'tax_id',
        ]

        labels = {
            'name': '店名',
            'address': '地址',
            'phone_number': '聯絡電話',
            'tax_id': '統編',
        }
