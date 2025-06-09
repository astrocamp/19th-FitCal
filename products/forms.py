from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

from .models import Product


class NoLabelClearableFileInput(ClearableFileInput):
    initial_text = _('目前檔案')
    input_text = _('更新檔案')
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
        ]
        labels = {
            'name': _('商品名稱'),
            'category': _('商品類別'),
            'image': _('商品圖片'),
            'description': _('商品介紹'),
            'calories': _('卡路里'),
            'quantity': _('可販售數量'),
            'price': _('價格'),
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
