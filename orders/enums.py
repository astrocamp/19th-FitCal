from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', '待付款'  #
    CANCELED = 'CANCELED', '已取消'  #
    PREPARING = 'PREPARING', '準備中'  #
    READY = 'READY', '餐點已備妥'  #
    COMPLETED = 'COMPLETED', '已完成'  #
    NO_SHOW = 'NO_SHOW', '未取餐'  # 未取餐
    CANCELED_REFUNDED = 'CANCELED_REFUNDED', '已取消 (退款)'


class PaymentMethod(models.TextChoices):
    CASH = 'cash', '現金'
    CREDIT_CARD = 'credit_card', '信用卡'
    LINE_PAY = 'line_pay', 'LINE Pay'


class PaymentStatus(models.TextChoices):
    UNPAID = 'unpaid', '未付款'
    PAID = 'paid', '已付款'
    REFUNDED = 'refunded', '已退款'
