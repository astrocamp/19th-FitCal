from datetime import timedelta

from django.core.exceptions import ValidationError
from django.forms import DateTimeInput, ModelForm, NumberInput
from django.utils import timezone
from django.utils.timezone import localtime

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
            'pickup_time': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.mode = kwargs.pop('mode', 'create')
        super().__init__(*args, **kwargs)

        now = timezone.localtime(timezone.now())
        rounded_time = next_10min(now)

        if self.mode == 'create':
            self.fields['pickup_time'].initial = rounded_time

            self.fields.pop('order_status')
            self.fields.pop('payment_status')
            self.fields.pop('total_price')

            # 設定預計取貨時間的日期選單不能選擇過去的日期
            self.fields['pickup_time'].widget.attrs['min'] = rounded_time.strftime(
                '%Y-%m-%dT%H:%M'
            )
            self.fields['pickup_time'].widget.attrs['max'] = (
                rounded_time + timedelta(days=7)
            ).strftime('%Y-%m-%dT%H:%M')

        if self.mode == 'update':
            saved_time = localtime(self.instance.pickup_time)
            self.fields['pickup_time'].widget.attrs['min'] = saved_time.strftime(
                '%Y-%m-%dT%H:%M'
            )
            self.fields['pickup_time'].widget.attrs['max'] = (
                saved_time + timedelta(hours=2)
            ).strftime('%Y-%m-%dT%H:%M')

            self.fields.pop('note')
            self.fields.pop('payment_method')
            self.fields.pop('total_price')

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

    def clean_pickup_time(self):
        pickup_time = self.cleaned_data['pickup_time']

        if self.mode == 'create':
            now = timezone.localtime(timezone.now())

            min_time = next_10min(now)
            if pickup_time < min_time:
                raise ValidationError('請選擇比現在晚至少10分鐘的時間')

            max_time = now + timedelta(days=7)
            if pickup_time > max_time:
                raise ValidationError('取貨時間不得超過7天後')

        elif self.mode == 'update':
            old_time = self.instance.pickup_time
            upper_bound = old_time + timedelta(hours=2)
            if not (old_time <= pickup_time <= upper_bound):
                raise ValidationError('請選擇在原訂時間後2小時內的時間')

        return pickup_time


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
            'quantity': NumberInput(attrs={'min': 1}),
        }
