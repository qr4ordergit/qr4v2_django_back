from rest_framework.serializers import ModelSerializer,Serializer
from . models import *


class RegistrationSerializer(ModelSerializer):
    
    class Meta:
        model = BusinessEntity
        fields = '__all__'
