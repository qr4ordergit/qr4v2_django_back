from django.contrib import admin
from restaurant.models import *
# Register your models here.


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name','description','status','updated_at','created_at']
    readonly_fields = ('referance',)