from django.forms import DateTimeInput, ModelForm, NumberInput, RadioSelect
from django.utils import timezone

from .models import Order, OrderItem
from .utils import round_up_to_next_10min


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'pickup_time',
            'note',
            'order_status',
            'payment_method',
            'payment_status',
            'total_price',
            'customize',
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
                    'step': '600',  # 每 10 分鐘一格
                }
            ),
            'payment_method': RadioSelect(
                choices=[
                    ('credit_card', '信用卡'),
                    ('mobile_payment', 'Line Pay'),
                    ('cash', '現金'),
                ]
            ),
            # 下拉式選單
            'order_status': RadioSelect(
                choices=[
                    ('pending', '待處理'),
                    ('in_progress', '處理中'),
                    ('completed', '已完成'),
                    ('canceled', '已取消'),
                ]
            ),
            'payment_status': RadioSelect(
                choices=[
                    ('unpaid', '未付款'),
                    ('paid', '已付款'),
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        mode = kwargs.pop('mode', 'create')
        super().__init__(*args, **kwargs)

        if mode == 'create':
            # 在建立訂單時，隱藏不需要的欄位
            self.fields.pop('order_status')
            self.fields.pop('payment_status')
            self.fields.pop('total_price')

        if mode == 'update':
            # 在更新訂單時，隱藏不需要的欄位
            # self.fields.pop('pickup_time')
            self.fields.pop('note')
            self.fields.pop('payment_method')
            self.fields.pop('total_price')
            self.fields.pop('customize')

        # 設定預計取貨時間的初始值為當前時間向上取整到最近的10分鐘
        # 這樣可以確保預計取貨時間至少在10分鐘後
        now = timezone.now()
        self.fields['pickup_time'].initial = round_up_to_next_10min(now)

    # 在儲存訂單時，依訂單項目計算總金額
    def save(self, commit=True):
        instance = super().save(commit=False)

        # 如果尚未儲存，先儲存 instance，確保有主鍵
        if commit and not instance.pk:
            instance.save()

        # 取得所有的 OrderItem
        order_items = instance.orderitem_set.all()

        # 計算總金額
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
