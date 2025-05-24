import uuid

from django.db import models

from stores.models import Store

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
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
