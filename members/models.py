import uuid

from django.db import models


# Create your models here.
class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    gender = models.CharField(
        max_length=10, choices=[('male', '男'), ('female', '女'), ('other', '不提供')]
    )
    date_of_birth = models.DateField()
    line_id = models.CharField(max_length=64, null=True, blank=True)
    google_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
