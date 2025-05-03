from django.forms import ModelForm

from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            # 'id',  不要放這個就不會有這個問題
            'name',
            'description',
            'calories',
            'quantity',
            'price',
            'customize',
        ]
        labels = {
            'id': '商品ID',
            'name': '商品名稱',
            'description': '商品介紹',
            'calories': '卡路里',
            'quantity': '可販售數量',
            'price': '價格',
            'customize': '客製化',
        }
