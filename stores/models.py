import uuid

from django.core.validators import RegexValidator
from django.db import models


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tax_id = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message='統編必須為8位數字')],
        blank=False,
    )
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
