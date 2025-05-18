import os
import sys
from pathlib import Path

import django
import pandas as pd

path = (
    Path(__file__).resolve().parent.parent
)  # 取得 FitCal 專案根目錄（manage.py 同層）
sys.path.insert(0, str(path))  # 加入根目錄到 sys.path，讓 Python 找得到 fitcal 模組

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitcal.settings')
django.setup()
from locations.models import Location

file_path = path.parent / 'FITCAL' / 'src' / 'files' / 'geocoded_addresses.csv'

init_df = pd.read_csv(file_path, encoding='utf-8-sig')

locations_df = init_df[
    ['name', 'latitude', 'longitude', 'city', 'district', 'detail']
].copy()

objs = [
    Location(
        name=row['name'],
        latitude=row['latitude'],
        longitude=row['longitude'],
        city=row['city'],
        district=row['district'],
        detail=row['detail'],
    )
    for idx, row in locations_df.iterrows()
]

Location.objects.bulk_create(objs)
