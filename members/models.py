import uuid

from django.core.validators import RegexValidator
from django.db import models

from stores.models import Store


class Member(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '不提供'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^09\d{8}$', message='手機號碼格式錯誤')],
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    line_id = models.CharField(max_length=64, null=True, blank=True)
    google_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    ordered_stores = models.ManyToManyField(
        Store, through='orders.Order', related_name='ordering_members'
    )
