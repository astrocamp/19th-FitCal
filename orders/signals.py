from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .enums import OrderStatus
from .models import Order


@receiver(pre_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """處理訂單狀態變更時的邏輯"""
    if not instance.pk:  # 新訂單
        return

    # 取得舊的訂單狀態
    try:
        old_instance = Order.objects.get(pk=instance.pk)
        old_status = old_instance.order_status
    except Order.DoesNotExist:
        return

    # 若狀態沒變，直接返回
    if old_status == instance.order_status:
        return

    # 處理狀態變更後的邏輯
    if instance.order_status == OrderStatus.COMPLETED:
        instance.completed_at = timezone.now()

    # 處理超時未取餐
    if (
        instance.order_status == OrderStatus.READY
        and instance.pickup_time < timezone.now()
    ):
        instance.order_status = OrderStatus.NO_SHOW

    # 處理未取餐訂單自動取消
    if (
        instance.order_status == OrderStatus.NO_SHOW
        and instance.pickup_time < timezone.now() - timezone.timedelta(hours=24)
    ):
        instance.order_status = OrderStatus.CANCELED
