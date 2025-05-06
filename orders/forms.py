from django.forms import DateTimeInput, ModelForm, NumberInput
from django.utils import timezone

from .models import Order, OrderItem
from .utils import next_10min


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'pickup_time',
            'order_status',
            'payment_method',
            'payment_status',
            'total_price',
            'note',
        ]
        labels = {
            'pickup_time': '預計取貨時間',
            'note': '備註',
            'order_status': '訂單狀態',
            'payment_method': '付款方式',
            'payment_status': '付款狀態',
            'total_price': '總金額',
            'customize': '客製化選項',
        }

        widgets = {
            'pickup_time': DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'create')
        super().__init__(*args, **kwargs)

        if mode == 'create':
            self.fields.pop('order_status')
            self.fields.pop('payment_status')
            self.fields.pop('total_price')

        if mode == 'update':
            self.fields.pop('note')
            self.fields.pop('payment_method')
            self.fields.pop('total_price')

        # initialize pickup_time
        now = timezone.now()
        rounded_time = next_10min(now)
        self.fields['pickup_time'].initial = rounded_time

        # 設定預計取貨時間的日期選單不能選擇過去的日期
        self.fields['pickup_time'].widget.attrs['min'] = rounded_time.strftime(
            '%Y-%m-%dT%H:%M'
        )

    # 在儲存訂單時，依訂單項目計算總金額
    def save(self, commit=True):
        instance = super().save(commit=False)

        # 如果尚未儲存，先儲存 instance，確保有主鍵
        if commit and not instance.pk:
            instance.save()

        order_items = instance.orderitem_set.all()

        total_price = sum(item.unit_price * item.quantity for item in order_items)
        instance.total_price = total_price

        if commit:
            instance.save()
        return instance


class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = ['unit_price', 'quantity']
        labels = {
            'unit_price': '單價',
            'quantity': '數量',
        }
        widgets = {
            'unit_price': NumberInput(attrs={'min': 0}),
            'quantity': NumberInput(attrs={'min': 0}),
        }
