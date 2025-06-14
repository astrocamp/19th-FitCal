from django.contrib import admin

from .models import Collection, Favorite, Member

admin.site.register(Member)
admin.site.register(Favorite)
admin.site.register(Collection)
