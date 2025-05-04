from django.db import models
import uuid


# Create your models here.

class Member(models.Model):
    GENDER_CHOICES = [
        ('Man', '男性'),
        ('Female', '女性'),
        ('Other', '其他'),
    ]
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20,blank=False)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username