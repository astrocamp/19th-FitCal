from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', _('處理中')
    CANCELED = 'CANCELED', _('已取消')
    PREPARING = 'PREPARING', _('準備中')
    READY = 'READY', _('餐點已備妥')
    COMPLETED = 'COMPLETED', _('已完成')
    NO_SHOW = 'NO_SHOW', _('未取餐')
    CANCELED_REFUNDED = 'CANCELED_REFUNDED', _('已取消並退款')


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', _('現金')
    LINE_PAY = 'LINE_PAY', 'LINE Pay'


class PaymentStatus(models.TextChoices):
    UNPAID = 'UNPAID', _('未付款')
    PAID = 'PAID', _('已付款')
    REFUNDED = 'REFUNDED', _('已退款')


class CancelBy(models.TextChoices):
    MEMBER = 'MEMBER', _('會員取消')
    STORE = 'STORE', _('店家取消')
    SYSTEM = 'SYSTEM', _('系統自動取消')
