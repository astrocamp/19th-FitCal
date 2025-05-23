import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
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


class Rating(models.Model):
    id = models.BigAutoField(primary_key=True)
    member = models.ForeignKey('members.Member', on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('member', 'store')

    def __str__(self):
        return f'{self.member.name} 給 {self.store.name} 的評分：{self.score} 分'
