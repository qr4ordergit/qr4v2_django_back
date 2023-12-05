from rest_framework.serializers import ModelSerializer
from . models import *
from rest_framework import serializers

class BusinessEntityRegistrationSerializer(ModelSerializer):
    owner = serializers.CharField(trim_whitespace=True)
    class Meta:
        model = BusinessEntity
        fields = ('owner','name','description',)


class QrSingatureSerializer(ModelSerializer):
    businessentity = serializers.CharField(trim_whitespace=True)
    class Meta:
        model = QrSingature
        fields = ('businessentity','table_name','qr_code','description','is_pin_enable','direct_order_table','is_online_order','bill_type')


class OutletSerializer(ModelSerializer):
    businessentity = serializers.IntegerField()
    class Meta:
        model = Outlet
        fields = (
            'name','description','phone_number','address','logo','businessentity'
        )
