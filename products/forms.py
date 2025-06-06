from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput

from .models import Product


class NoLabelClearableFileInput(ClearableFileInput):
    initial_text = '目前檔案'
    input_text = '更新檔案'
    clear_checkbox_label = ''


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'image',
            'description',
            'calories',
            'quantity',
            'price',
            'customize',
        ]
        labels = {
            'name': '商品名稱',
            'category': '商品類別',
            'image': '商品圖片',
            'description': '商品介紹',
            'calories': '卡路里',
            'quantity': '可販售數量',
            'price': '價格',
            'customize': '客製化',
        }
        widgets = {
            'image': NoLabelClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        # 把 store 從 kwargs 拿出來
        store = kwargs.pop('store', None)
        initial_category = kwargs.pop('category', None)  # 把傳入的 category 拿出來
        super().__init__(*args, **kwargs)
        if store:
            self.fields['category'].queryset = store.categories.order_by('name')
        if initial_category:
            self.fields['category'].initial = initial_category
