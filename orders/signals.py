from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .enums import CancelBy, OrderStatus
from .models import Order
from .utils import (
    build_line_order_created_message,
    build_line_order_status_message,
    push_line_message,
)


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
        instance.canceled_by = CancelBy.SYSTEM


@receiver(post_save, sender=Order)
def send_line_message_when_order_created(sender, instance, created, **kwargs):
    if not created:
        return  # 只推播新建立的訂單

    user = instance.member.user
    try:
        account = SocialAccount.objects.get(user=user, provider='line')
        line_user_id = account.uid
        msg = build_line_order_created_message(instance)
        push_line_message(line_user_id, msg)
    except SocialAccount.DoesNotExist:
        pass  # 沒有 LINE 帳號的就跳過


@receiver(post_save, sender=Order)
def handle_order_notifications(sender, instance, created, **kwargs):
    if created:  # 新訂單由另一個 signal 處理
        return

    try:
        user = instance.member.user
        account = SocialAccount.objects.get(user=user, provider='line')
        line_user_id = account.uid

        # 如果是取消狀態，只在有明確的取消來源時才發送通知
        if instance.order_status == OrderStatus.CANCELED:
            if instance.canceled_by:  # 只有在有取消來源時才發送
                message = build_line_order_status_message(instance)
                push_line_message(line_user_id, message)

        # 其他狀態正常發送
        elif instance.order_status in [OrderStatus.READY, OrderStatus.COMPLETED]:
            message = build_line_order_status_message(instance)
            push_line_message(line_user_id, message)

    except SocialAccount.DoesNotExist:
        pass
