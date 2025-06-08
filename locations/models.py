from django.contrib.gis.db import models as gis_models
from django.db import models


# 經緯度
class Location(models.Model):
    store = models.OneToOneField(
        'stores.Store', on_delete=models.CASCADE, related_name='location'
    )
    point = gis_models.PointField(geography=True)
