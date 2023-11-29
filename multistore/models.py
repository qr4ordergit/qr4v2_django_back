from django.db import models
from string import digits,hexdigits,ascii_uppercase
from random import choices
import uuid
import time
from authenticator.models import CustomUser

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
    owner = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="owner",null=True)
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

def create_session_pin():
    timestamp = str(time.time()).encode('utf-8')
    unique_id = hash(timestamp)
    abs_unique_id = abs(unique_id)
    code = ''.join(choices(str(abs_unique_id),k=4))
    return code


#table session
class OrderSession(CommonFields):
    restaurant_table = models.ForeignKey(QrSingature, on_delete=models.CASCADE, related_name='qrsingature_table')
    session_uuid = models.UUIDField(unique=True, default = uuid.uuid4,editable = False)
    bill_no = models.IntegerField(blank=True,unique=True)
    session_nickname = models.CharField(max_length=200, null=True, blank=True)
    session_pin = models.CharField(max_length=6,default=create_session_pin)
    is_bill_paid = models.BooleanField(default=False)
    no_of_ordered_placed = models.IntegerField(default=0)
    no_of_ordered_confirmed = models.IntegerField(default=0)
    no_of_ordered_cancel = models.IntegerField(default=0)
    session_order_number = models.CharField(max_length=20, null=True, blank=True)
    is_session_active = models.BooleanField(default=True)
    amount = models.FloatField(default=None, null=True, blank=True)
    total_tip = models.FloatField(default=0)


#order_summary
class OrderDetails(CommonFields):
    table_session = models.ForeignKey(OrderSession, on_delete=models.CASCADE, related_name="session_order_details")
    item_total_price = models.FloatField()
    item_price = models.FloatField()
    item_unit = models.CharField(max_length=10,default="")
    order_serial_no = models.IntegerField()

    def __str__(self) -> str:
        return self.item_total_price + self.item_price 


    

    
