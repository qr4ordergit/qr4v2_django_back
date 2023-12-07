from rest_framework import serializers 
from authenticator.models import Permission,UserLevel,Operation
from multistore.models import *


class UserLevel_Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserLevel
        fields = ('name',)

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ('name',)


class Permission_Serializer(serializers.ModelSerializer):
     user_level = UserLevel_Serializer()
     operation = OperationSerializer(many=True)

     class Meta: 
        model = Permission
        fields = ['name', 'operation', 'user_level'] 
      

class Outlet_Serializer(serializers.ModelSerializer):
        
    class Meta:
        model = Outlet
        fields = ('id','name','outlet_code','description',
                  'businessentity','logo','phone_number','qr_code','address')