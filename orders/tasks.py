from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now

from orders.models import Order


@shared_task
def check_overdue_orders():
    """定期檢查已逾時未取餐訂單，並發送 Email 通知給會員"""
    overdue_orders = Order.objects.filter(
        order_status='PENDING',
        pickup_time__lt=now(),
    )

    sent_count = 0
    for order in overdue_orders:
        if order.member and order.member.email:
            try:
                send_mail(
                    subject='【FitCal】您有尚未完成的訂單',
                    message=(
                        f'親愛的會員您好，您有一筆原訂於 {order.pickup_time.strftime("%Y-%m-%d %H:%M")} 取餐的訂單尚未完成，'
                        '請儘快前往取餐或聯繫我們以獲取更多資訊。'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.member.email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                # 可寫 log 或報錯紀錄
                print(f'寄信失敗：{e}')

    return f'{sent_count}/{overdue_orders.count()} overdue orders notified.'
