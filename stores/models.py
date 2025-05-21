import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from users.models import User


# 重新定義添加軟刪除後的搜尋行為
class StoreManager(models.Manager):
    def get_queryset(self):
        # 只回傳沒被軟刪除的 Member
        return super().get_queryset().filter(deleted_at__isnull=True)


class Store(models.Model):
    name = models.CharField(max_length=50)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    opening_time = models.TimeField(default='06:00')
    closing_time = models.TimeField(default='00:00')
    tax_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message='統編必須為8位數字')],
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

    def __str__(self):
        return self.name


class Rating(models.Model):
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'store'], name='unique_member_store_rating'
            )
        ]

    def __str__(self):
        return f'{self.member.name} 給 {self.store.name} 的評分：{self.score} 分'
