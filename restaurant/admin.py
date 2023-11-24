from django.contrib import admin
from restaurant.models import *
# Register your models here.


@admin.register(BusinessEntity)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name','description','status','updated_at','created_at']
    readonly_fields = ('referance',)