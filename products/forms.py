from django.forms import ModelForm

from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'image',
            'description',
            'calories',
            'quantity',
            'price',
            'customize',
        ]
        labels = {
            'name': '商品名稱',
            'image': '商品圖片',
            'description': '商品介紹',
            'calories': '卡路里',
            'quantity': '可販售數量',
            'price': '價格',
            'customize': '客製化',
        }
