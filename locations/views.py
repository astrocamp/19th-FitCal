import os
from pathlib import Path

import environ
import requests
from django.http import JsonResponse
from django.shortcuts import render
from geopy.distance import geodesic

from .models import Location


# Create your views here.
def index(req):
    return render(req, 'locations/index.html', {})


def search_addr(req):
    if req.method == 'POST':
        address = req.POST.get('address')
        # result = geocode_address(address)
        result = {'latitude': 25.042422, 'longitude': 121.513897}
        if result:
            print(f'search--------{result}----------search')
            return JsonResponse(result)
        else:
            return JsonResponse({'error': '無法找到地址'}, status=404)


def search_store(req):
    if req.method == 'POST':
        lat = float(req.POST.get('latitude'))
        lng = float(req.POST.get('longitude'))
        rad = float(req.POST.get('radius'))
        center = (lat, lng)
        result = []
        for loc in Location.objects.all():
            target = (loc.latitude, loc.longitude)
            distance_km = geodesic(center, target).km
            if distance_km <= rad:
                result.append(
                    {
                        'name': loc.name,
                        'latitude': loc.latitude,
                        'longitude': loc.longitude,
                        'distance_km': round(distance_km, 1),
                    }
                )
        return render(req, 'locations/result.html', {'radius': rad, 'result': result})


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

    if data.get('results'):
        result = data['results'][0]
        print(f'function------------------\n{result}----------------function')
        position = result['position']
        addr = result['address']

        return {
            'latitude': position['lat'],  # 緯度
            'longitude': position['lon'],  # 經度
            'city': addr.get('countrySubdivision', '')  # 市
            + addr.get('municipalitySubdivision', '')  # 區
            + addr.get('streetName', '')  # 路名
            + addr.get('streetNumber', ''),  # 門牌號
        }

    return None
