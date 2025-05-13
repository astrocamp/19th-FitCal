import uuid

from django.db import models

from stores.models import Store


# Create your models here.


def product_image_upload_path(instance, filename):
    # instance 是 Product model 的物件
    # 將圖片存到 products/<product_id>/<filename>
    return f'products/{instance.id}/{filename}'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField()
    calories = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    customize = models.TextField(null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
