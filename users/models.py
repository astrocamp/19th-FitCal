import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('必須提供電子郵件地址'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser 必須設 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser 必須設 is_superuser=True')

        return self.create_user(
            email, password, **extra_fields
        )  # 不影響運作可刪 create_superuser()


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('使用者的ID'),
    )
    username = None  # 移除 username
    email = models.EmailField(unique=True, help_text='example@mail.com')

    ROLE_CHOICES = [
        ('member', 'Member'),
        ('store', 'Store'),
    ]
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='member', blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def is_member(self):
        return self.role == 'member'

    @property
    def is_store(self):
        return self.role == 'store'

    def __str__(self):
        return self.email
