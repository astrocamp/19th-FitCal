from django.contrib import admin

from .models import Category, Rating, Store

admin.site.register(Store)
admin.site.register(Rating)
admin.site.register(Category)
