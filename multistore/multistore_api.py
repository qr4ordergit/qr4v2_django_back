from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from . serializers import RegistrationSerializer
import json


class Registrations(APIView):
    serializer_class = RegistrationSerializer

    def get(self,request):
        return Response({"message":"get api"},status=status.HTTP_200_OK)

    def post(self,request):
        return Response({"message":"post api"})
    