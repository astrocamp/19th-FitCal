import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import User


# 重新定義添加軟刪除後的搜尋行為
class StoreManager(models.Manager):
    def get_queryset(self):
        # 只回傳沒被軟刪除的 Member
        return super().get_queryset().filter(deleted_at__isnull=True)


class Store(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cover_image = models.ImageField(upload_to='store_covers/', blank=True, null=True)
    logo_image = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    opening_time = models.TimeField(default='06:00')
    closing_time = models.TimeField(default='00:00')
    tax_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message=_('統編必須為8位數字'))],
        blank=False,
    )

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_email = models.CharField(max_length=254, null=True, blank=True)

    objects = StoreManager()
    # 用all_objects可以查看全部包含被軟刪除的資料
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        if self.user and not self.deleted_email:
            self.deleted_email = self.user.email
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at', 'deleted_email'])
        self.products.update(deleted_at=self.deleted_at)
        self.user.delete(using=using, keep_parents=keep_parents)
        self.categories.all().delete()

    def __str__(self):
        return self.name

    @property
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return 'https://5x-fitcal.s3.ap-northeast-1.amazonaws.com/media/store_covers/default-cover.webp'  # S3的網址

    @property
    def logo_url(self):
        if self.logo_image:
            return self.logo_image.url
        return 'https://5x-fitcal.s3.ap-northeast-1.amazonaws.com/media/store_logos/default-logo.webp'  # S3的網址


class Rating(models.Model):
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, null=True, blank=True
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order'], name='unique_rating_per_order')
        ]

    def __str__(self):
        return f'{self.member.name} 評分訂單 {self.order.order_number} 的 {self.store.name}：{self.score} 分'


class Category(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='categories'
    )
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['store', 'name'], name='unique_category_store'
            )
        ]

    def __str__(self):
        return f'{self.name}'
