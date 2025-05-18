from django.db import models


# 經緯度
class Location(models.Model):
    # 測試功能，先不和store做一對一關聯
    # store = models.OneToOneField(
    #     'stores.Store', on_delete=models.CASCADE, related_name='location'
    # )
    name = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    detail = models.CharField(max_length=255)
    # source = models.CharField(max_length=50, blank=True, null=True)  # API 來源
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.city}{self.district}{self.detail}:{self.latitude},{self.longitude}'
        )
