import uuid

from django.contrib.auth.models import User
from django.db import models


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='store'
    )  # 關聯 AUTH
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    tax_id = models.TextField(max_length=8)
