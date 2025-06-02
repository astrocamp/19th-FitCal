import uuid

from django.db import models
from django.utils import timezone

from stores.models import Store


class ProductManager(models.Manager):
    def get_queryset(self):
        # 只回傳沒被軟刪除的 Member
        return super().get_queryset().filter(deleted_at__isnull=True)


# Create your models here.


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='products/', null=False, blank=False, default=''
    )
    description = models.TextField()
    calories = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField()
    customize = models.TextField(null=True, blank=True)
    store = models.ForeignKey(
        Store, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = ProductManager()
    # 用all_objects可以查看全部包含被軟刪除的資料
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['deleted_at'])

    def __str__(self):
        return self.name
