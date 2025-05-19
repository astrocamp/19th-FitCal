from django.db import transaction

from .fsm import OrderFSM
from .models import Order


class OrderService:
    """訂單服務層"""

    def __init__(self, order_id):
        self.order = Order.objects.get(id=order_id)
        self.fsm = OrderFSM(self.order)

    @transaction.atomic
    def cancel_order(self):
        """取消訂單"""
        return self.fsm.cancel()

    @transaction.atomic
    def prepare_order(self):
        """開始準備訂單"""
        return self.fsm.prepare()

    @transaction.atomic
    def mark_order_ready(self):
        """標記訂單準備完成"""
        return self.fsm.mark_ready()

    @transaction.atomic
    def complete_order(self):
        """完成訂單（顧客取餐）"""
        return self.fsm.complete()

    @transaction.atomic
    def mark_order_no_show(self):
        """標記訂單為未取餐"""
        return self.fsm.mark_no_show()
