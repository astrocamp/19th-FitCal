import os
import re
from pathlib import Path

import environ
import requests
from django.contrib.gis.geos import Point
from django.http import JsonResponse

from .models import Location


def geocode_address(address):
    BASE_DIR = Path(__file__).resolve().parent
    env = environ.Env()
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    url = f'https://api.tomtom.com/search/2/geocode/{address}.json'
    params = {
        'key': env('TOMTOM_API_KEY'),
        'limit': 1,
        'countrySet': 'TW',
        'language': 'zh-TW',
    }

    response = requests.get(url, params=params)
    data = response.json()
    print(data)
    if data.get('results'):
        result = data['results'][0]
        position = result['position']
        return {
            'latitude': position['lat'],  # 緯度
            'longitude': position['lon'],  # 經度
        }

    return None


def add_location(store, addr):
    match = re.search(r'號', addr)
    if match:
        addr[: match.end()]
    geo_data = geocode_address(addr)
    if geo_data:
        point = Point(geo_data['longitude'], geo_data['latitude'])
        Location.objects.update_or_create(store=store, defaults={'point': point})


def store_distance(request):
    lat = float(request.GET.get('lat'))
    lng = float(request.GET.get('lng'))
    store_id = request.GET.get('store_id', None)
    print(store_id)
    if store_id:
        # 原生SQL語法，爲了取得非直線距離，所以在直線距離的基礎上*1.4倍，提供估算出來的路線距離
        sql = """
        SELECT id, point,
            ST_Distance(
                point,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            ) / 700.0 AS distance_km
        FROM locations_location
        WHERE store_id = %s
        """
        locations = Location.objects.raw(sql, [lng, lat, store_id])
        for loc in locations:
            print(loc.distance_km)
            return JsonResponse({'distance_km': f'{loc.distance_km:.1f}'})
    else:
        sql = """
        SELECT id,
            ST_Distance(
                point,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            ) / 700.0 AS distance_km
        FROM locations_location
        """
        locations = Location.objects.raw(sql, [lng, lat])
        data = {str(loc.store_id): f'{loc.distance_km:.1f}' for loc in locations}
        return JsonResponse(data)
