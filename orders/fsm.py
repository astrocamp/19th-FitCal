from django.utils import timezone

from .enums import OrderStatus, PaymentMethod, PaymentStatus


class OrderFSM:
    """訂單狀態機定義"""

    def __init__(self, order):
        self.order = order

    @property
    def current_state(self):
        return self.order.order_status

    def _can_transition(self, from_states, to_state):
        return self.current_state in from_states

    def transition(self, to_state):
        """執行狀態轉換"""
        self.order.order_status = to_state
        self._handle_payment_status()
        self.order.save()

    def _handle_payment_status(self):
        """處理訂單狀態變更時的付款狀態同步"""
        if self.order.order_status == OrderStatus.CANCELED_REFUNDED:
            self.order.payment_status = PaymentStatus.REFUNDED
        elif self.order.order_status == OrderStatus.CANCELED:
            if self.order.payment_status == PaymentStatus.PAID:
                self.order.payment_status = PaymentStatus.REFUNDED

    def can_cancel(self, by_store=False):
        """
        檢查是否可以取消訂單

        Args:
            by_store (bool): True if cancellation is initiated by store, False if by member
        """
        allowed_states = (
            [OrderStatus.PENDING, OrderStatus.PREPARING]
            if by_store
            else [OrderStatus.PENDING]
        )
        return self._can_transition(allowed_states, OrderStatus.CANCELED)

    def cancel(self, by_store=False):
        """
        取消訂單

        Args:
            by_store (bool): True if cancellation is initiated by store, False if by member
        """
        if self.can_cancel(by_store):
            self.transition(OrderStatus.CANCELED)
            return True
        return False

    def can_prepare(self):
        """檢查是否可以開始準備"""
        is_valid_state = self._can_transition(
            [OrderStatus.PENDING], OrderStatus.PREPARING
        )
        can_process = (
            self.order.payment_status == PaymentStatus.PAID
            or self.order.payment_method == PaymentMethod.CASH
        )
        return is_valid_state and can_process

    def prepare(self):
        """開始準備訂單"""
        if self.can_prepare():
            self.transition(OrderStatus.PREPARING)
            return True
        return False

    def can_mark_ready(self):
        """檢查是否可以標記為準備完成"""
        return self._can_transition([OrderStatus.PREPARING], OrderStatus.READY)

    def mark_ready(self):
        """標記訂單準備完成"""
        if self.can_mark_ready():
            self.transition(OrderStatus.READY)
            return True
        return False

    def can_complete(self):
        """檢查是否可以完成訂單"""
        return self._can_transition([OrderStatus.READY], OrderStatus.COMPLETED)

    def complete(self):
        """完成訂單"""
        if self.can_complete():
            self.order.completed_at = timezone.now()
            self.transition(OrderStatus.COMPLETED)
            return True
        return False

    def can_mark_no_show(self):
        """檢查是否可以標記為未取餐"""
        is_valid_state = self._can_transition([OrderStatus.READY], OrderStatus.NO_SHOW)
        is_timeout = (
            timezone.now() - self.order.pickup_time
        ).total_seconds() > 24 * 3600
        return is_valid_state and is_timeout

    def mark_no_show(self):
        """標記為未取餐"""
        if self.can_mark_no_show():
            self.transition(OrderStatus.NO_SHOW)
            return True
        return False
