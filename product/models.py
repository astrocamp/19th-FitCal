import uuid

from django.db import models


# Create your models here.
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    description = models.TextField()
    calories = models.DecimalField(max_digits=5, decimal_places=1)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    customize = models.TextField(null=True, blank=True)
