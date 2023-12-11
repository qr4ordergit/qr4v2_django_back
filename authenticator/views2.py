from rest_framework.views import APIView
from rest_framework.response import Response
from authenticator.serializers import Permission_Serializer
from authenticator.models import Permission


class PermissionView(APIView):
    serializer_class = Permission_Serializer

    def get(self,request):
        permission = Permission.objects.all()
        permission = self.serializer_class(permission,many=True).data
        return Response({"data":permission})
    

    
