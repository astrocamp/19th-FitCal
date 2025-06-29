from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.forms import DateTimeInput, ModelForm, NumberInput
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

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
            'pickup_time': _('預計取貨時間'),
            'note': _('備註'),
            'order_status': _('訂單狀態'),
            'payment_method': _('付款方式'),
            'payment_status': _('付款狀態'),
            'total_price': _('總金額'),
            'customize': _('客製化選項'),
        }

        widgets = {
            'pickup_time': DateTimeInput(
                attrs={
                    'type': 'text',
                    'class': 'flatpickr-input',
                },
                format='%Y-%m-%dT%H:%M',
            )
        }

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop('store', None)
        self.mode = kwargs.pop('mode', 'create')
        super().__init__(*args, **kwargs)

        self.fields['pickup_time'].widget.attrs.update(
            {
                'x-model': 'formData.pickup_time',
            }
        )

        self.fields['payment_method'].widget.attrs.update(
            {
                'x-model': 'formData.payment_method',
            }
        )

        now = timezone.localtime(timezone.now())
        rounded_time = next_10min(now)

        if self.mode == 'create':
            self.fields['pickup_time'].initial = self._get_next_valid_time(rounded_time)

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

    def _get_next_valid_time(self, current_time):
        """根據店家營業時間，回傳下個合法取餐時間"""
        if not self.store:
            return current_time  # 沒有 store 就不處理

        opening_time = self.store.opening_time  # time object
        closing_time = self.store.closing_time  # time object
        current_store_time = current_time.time()

        # 若 current_time 在營業時間區間內（含開，不含關） → 合法
        if opening_time <= current_store_time < closing_time:
            return current_time

        # 早於開店 → 今日開店時間
        if current_store_time < opening_time:
            return datetime.combine(current_time.date(), opening_time)

        # 晚於打烊 → 明日開店時間
        next_day = current_time.date() + timedelta(days=1)
        return datetime.combine(next_day, opening_time)

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

    # 針對 pickup_time 欄位的後端驗證
    def clean_pickup_time(self):
        pickup_time = self.cleaned_data['pickup_time']

        if self.mode == 'create':
            now = timezone.localtime(timezone.now())

            min_time = next_10min(now)
            if pickup_time < min_time:
                raise ValidationError(_('請選擇比現在晚至少10分鐘的時間'))

            max_time = now + timedelta(days=7)
            if pickup_time > max_time:
                raise ValidationError(_('取貨時間不得超過7天後'))

        elif self.mode == 'update':
            old_time = self.instance.pickup_time
            upper_bound = old_time + timedelta(hours=2)
            if not (old_time <= pickup_time <= upper_bound):
                raise ValidationError(_('請選擇在原訂時間後2小時內的時間'))

        return pickup_time


class OrderItemForm(ModelForm):
    class Meta:
        model = OrderItem
        fields = ['unit_price', 'quantity']
        labels = {
            'unit_price': _('單價'),
            'quantity': _('數量'),
        }
        widgets = {
            'unit_price': NumberInput(attrs={'min': 0}),
            'quantity': NumberInput(attrs={'min': 1}),
        }
