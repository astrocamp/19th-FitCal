import uuid

from django.core.validators import RegexValidator
from django.db import models

from users.models import User


class Store(models.Model):
    name = models.CharField(max_length=50)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
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

    def __str__(self):
        return self.name
