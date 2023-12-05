from django.contrib import admin
from multistore.models import *
# Register your models here.

@admin.register(BusinessEntity)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name','description','updated_at','created_at']
    readonly_fields = ('referance',)


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ['name',]
    readonly_fields = ('outlet_code',)
