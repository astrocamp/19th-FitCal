from django.forms import IntegerField, ModelForm, NumberInput
from django.utils.translation import gettext_lazy as _

from .models import Cart, CartItem


class CartForm(ModelForm):
    class Meta:
        model = Cart
        fields = ['store', 'note']
        labels = {
            'store': _('商店'),
            'note': _('備註'),
        }


class CartItemForm(ModelForm):
    quantity = IntegerField(
        min_value=1,
        widget=NumberInput(attrs={'min': 1, 'step': 1}),
        error_messages={
            'min_value': _('數量不能小於 1'),
            'invalid': _('請輸入正整數'),
        },
    )

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'customize']
        labels = {
            'product': _('產品'),
            'quantity': _('數量'),
            'customize': _('客製化'),
        }
