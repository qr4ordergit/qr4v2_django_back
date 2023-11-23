from django.db import models
from string import digits,hexdigits,ascii_uppercase
from random import choices
import uuid

# class Country(models.Model):
#     NAME = models.CharField(max_length=250, null=False, blank=False)
#     LANGUAGE = models.CharField(max_length=250, null=False, blank=False)
#     is_active = models.BooleanField(default=True)
    

# class Currency(models.Model):
#     NAME = models.CharField(max_length=250, null=False, blank=False)   

# class Timezone(models.Model):
#     TimeZone = models.CharField(max_length=100)
#     Region = models.CharField(max_length=100)
#     UTCOffset = models.CharField(max_length=100)


class CommonFields(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    class Meta: 
        abstract = True

def generate_code():
    code = ''.join(choices(ascii_uppercase+digits,k = 8))
    if BusinessEntity.objects.filter(referance=code).exists():
        return generate_code
    return code


class BusinessEntity(CommonFields):
    id = models.BigAutoField(primary_key = True)
    referance = models.CharField(max_length=300,default=generate_code)
    name = models.CharField(max_length=255)
    description = models.TextField(default='',null=True,blank=True)
    status = models.BooleanField(default=False)
    # timezone = models.ForeignKey(Timezone, on_delete=models.CASCADE, related_name='restaurant_timezone', null=True)
    # country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='restaurant_country',default='',null=True,blank=True)
    # currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='restaurant_currency',default='1',null=True, blank=True)
    def __str__(self) -> str:
        return self.name

class QrSingature(CommonFields):
    restaurant = models.ForeignKey(BusinessEntity, on_delete=models.CASCADE, related_name="restauranttable_restaurant",null=True, blank=True)
    table_name = models.CharField(max_length=20,null=True, blank=True)
    qr_code = models.FileField(null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)
    is_pin_enable = models.BooleanField(default=False)
    direct_order_table = models.BooleanField(default=False)
    is_online_order = models.BooleanField(default=False)
    bill_type = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return self.table_name


#table session
# class OrderSession(models.Model):
#     pass

#ordersummary
# class OrderDetails(models.Model):
#     pass
    #   status = pending,configme,