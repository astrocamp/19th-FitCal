import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from products.models import Product
from stores.models import Store
from users.models import User


class Member(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '不提供'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^09\d{8}$', message='手機號碼格式錯誤')],
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
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


class Favorite(models.Model):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='favorite_records'
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'store')  # 防止重複收藏

    def __str__(self):
        return f'{self.member.name} 收藏了 {self.store.name}'


class Collection(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['member', 'product'], name='unique_member_product')
        ]

    def __str__(self):
        return f'{self.member} 收藏了 {self.product}'
