from celery import shared_task
from django.utils.timezone import now

from orders.models import Order
from orders.utils import send_order_reminder_email


@shared_task
def check_overdue_orders():
    """定期檢查已逾時未取餐且尚未提醒的訂單，並發送 Email 通知給會員"""
    overdue_orders = Order.objects.filter(
        order_status='READY',
        pickup_time__lt=now(),
        reminder_sent_at__isnull=True,
    )

    sent_count = 0
    for order in overdue_orders:
        try:
            if send_order_reminder_email(order):
                order.reminder_sent_at = now()
                order.save(update_fields=['reminder_sent_at'])
                sent_count += 1
        except Exception as e:
            print(f'寄信失敗：{e}')  # 或用 logger.warning()

    return f'{sent_count}/{overdue_orders.count()} overdue orders notified.'
