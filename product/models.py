import uuid

from django.db import models


# Create your models here.
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    calories = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    customize = models.TextField(null=True, blank=True)
