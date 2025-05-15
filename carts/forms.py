from django.forms import IntegerField, ModelForm, NumberInput, inlineformset_factory

from .models import Cart, CartItem


class CartForm(ModelForm):
    class Meta:
        model = Cart
        fields = ['store', 'note', 'total_price']
        labels = {
            'store': '商店',
            'note': '備註',
            'total_price': '總金額',
        }


class CartItemForm(ModelForm):
    quantity = IntegerField(
        min_value=1,
        widget=NumberInput(attrs={'min': 1, 'step': 1}),
        error_messages={
            'min_value': '數量不能小於 1',
            'invalid': '請輸入正整數',
        },
    )

    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'customize']
        labels = {
            'product': '產品',
            'quantity': '數量',
            'customize': '客製化',
        }


NewCartItemFormSet = inlineformset_factory(
    Cart,
    CartItem,
    form=CartItemForm,
    fields=['product', 'quantity', 'customize'],
    can_delete=False,
    extra=1,  # 顯示一筆空白表單
)

EditCartItemFormSet = inlineformset_factory(
    Cart,
    CartItem,
    form=CartItemForm,
    fields=['product', 'quantity', 'customize'],
    can_delete=False,
    extra=0,
)
