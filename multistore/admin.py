from django.contrib import admin
from multistore.models import *
# Register your models here.


@admin.register(BusinessEntity)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name','description','updated_at','created_at']
    readonly_fields = ('referance',)