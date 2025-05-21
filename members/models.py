import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils import timezone

from products.models import Product
from stores.models import Store


# 重新定義添加軟刪除後的搜尋行為
class MemberManager(models.Manager):
    def get_queryset(self):
        # 只回傳沒被軟刪除的 Member
        return super().get_queryset().filter(deleted_at__isnull=True)


class Member(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '不提供'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='member',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^09\d{8}$', message='手機號碼格式錯誤')],
    )
    gender = models.CharField(
        max_length=10, null=True, blank=True, choices=GENDER_CHOICES
    )
    date_of_birth = models.DateField(null=True, blank=True)
    line_id = models.CharField(max_length=64, null=True, blank=True)
    google_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorite = models.ManyToManyField(
        Store, through='Favorite', related_name='favorited_by'
    )
    ordered_stores = models.ManyToManyField(
        Store, through='orders.Order', related_name='ordering_members'
    )
    favorite_products = models.ManyToManyField(
        Product,
        through='Collection',  # 使用中介表
        related_name='favorited_by',  # 反向關聯名稱，讓 product.favorited_by.all() 可用
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_email = models.CharField(max_length=254, null=True, blank=True)

    objects = MemberManager()
    # 用all_objects可以查看全部包含被軟刪除的資料
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        if self.user and not self.deleted_email:
            self.deleted_email = self.user.email
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at', 'deleted_email'])
        self.user.delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return f'{self.member.name} 收藏了 {self.store.name}'


class Favorite(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='favorite_records'
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['member', 'store'],
                name='unique_member_store',
                condition=Q(deleted_at__isnull=True),
            )
        ]


class Collection(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['member', 'product'],
                name='unique_member_product',
                condition=Q(deleted_at__isnull=True),
            )
        ]

    def __str__(self):
        return f'{self.member} 收藏了 {self.product}'
