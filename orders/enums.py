from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', '處理中'
    CANCELED = 'CANCELED', '已取消'
    PREPARING = 'PREPARING', '準備中'
    READY = 'READY', '餐點已備妥'
    COMPLETED = 'COMPLETED', '已完成'
    NO_SHOW = 'NO_SHOW', '未取餐'
    CANCELED_REFUNDED = 'CANCELED_REFUNDED', '已取消並退款'


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', '現金'
    CREDIT_CARD = 'CREDIT_CARD', '信用卡'
    LINE_PAY = 'LINE_PAY', 'LINE Pay'


class PaymentStatus(models.TextChoices):
    UNPAID = 'UNPAID', '未付款'
    PAID = 'PAID', '已付款'
    REFUNDED = 'REFUNDED', '已退款'


class CancelBy(models.TextChoices):
    MEMBER = 'MEMBER', '會員取消'
    STORE = 'STORE', '店家取消'
    SYSTEM = 'SYSTEM', '系統自動取消'
