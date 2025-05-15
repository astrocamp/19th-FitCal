import uuid

from django.core.validators import RegexValidator
from django.db import models

<<<<<<< HEAD
from stores.models import Store
=======
from users.models import User
>>>>>>> 4385fbb (feat: Add one-to-one relations: users-members, users-stores; add name fields)


class Member(models.Model):
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '不提供'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^09\d{8}$', message='手機號碼格式錯誤')],
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    line_id = models.CharField(max_length=64, null=True, blank=True)
    google_id = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

<<<<<<< HEAD
    ordered_stores = models.ManyToManyField(
        Store, through='orders.Order', related_name='ordering_members'
    )
=======
    def __str__(self):
        return self.name
>>>>>>> 4385fbb (feat: Add one-to-one relations: users-members, users-stores; add name fields)
