from rest_framework.views import APIView
from django.utils import translation
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import  JsonResponse
from rest_framework import status as http_status
import polib
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from . serializers import ( 
    BusinessEntityRegistrationSerializer,
    QrSingatureSerializer
)
from rest_framework.authentication import  BasicAuthentication
import json
from rest_framework.permissions import IsAuthenticated
from multistore.custom_authetication import CustomAuthentication

class LanguageDetails(APIView):
    def checkLang(self,lang):
        if lang in[code for code, _ in settings.LANGUAGES]:
            return True
        return False

    def get(self,request,lang):

        if not self.checkLang(lang):
            return JsonResponse({'message':"Language not present in the system"})
        
        translation.activate(lang)
        translations = {}
        lang_clean = "en_US" if lang == "en-us" else lang
        
        po = polib.pofile(f"locale/{lang_clean}/LC_MESSAGES/django.po")

        for entry in po:
            translations[str(entry.msgid)] = _(str(entry.msgid))
        return JsonResponse(translations)
    
class LanguageCrud(APIView):

    def checkLang(self,lang):
        if lang in[code for code, _ in settings.LANGUAGES]:
            return True
        return False

    def get(self,request,lang):

        if not self.checkLang(lang):
            return JsonResponse({'message':"Language not present in the system"},http_status.HTTP_404_NOT_FOUND)
        
        translation.activate(lang)
        translations = {}
        lang_clean = "en_US" if lang == "en-us" else lang
        
        po = polib.pofile(f"locale/{lang_clean}/LC_MESSAGES/django.po")

        for entry in po:
            translations[str(entry.msgid)] = _(str(entry.msgid))
        return JsonResponse(translations)
   
    def post(self,request,lang):

        if not self.checkLang(lang):
            return JsonResponse({'message':"Language not present in the system"},http_status.HTTP_404_NOT_FOUND)

        data = request.data        
        po_file=polib.pofile(f"D:/qr4order_new/qr4v2_django_back/locale/{lang}/LC_MESSAGES/django.po")

        try:
            for msgid, msgstr in data.items():
                po_obj = po_file.find(msgid)
                if po_obj:
                    po_obj.msgstr = msgstr                    
                else:
                    new_entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
                    po_file.append(new_entry)
            po_file.save()
            po_file.save_as_mofile(f"D:/qr4order_new/qr4v2_django_back/locale/{lang}/LC_MESSAGES/django.mo")
            return JsonResponse({'success': True, 'message': 'Translation Updated Successfully'},http_status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error creating and updating translations'},http_status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self,request,lang):

        if not self.checkLang(lang):
            return JsonResponse({'message':"Language not present in the system"},http_status.HTTP_404_NOT_FOUND)
        
        data=request.data
        po_file=polib.pofile(f"D:/qr4order_new/qr4v2_django_back/locale/{lang}/LC_MESSAGES/django.po")

        try:
            for msgid,msgstr in data.items():
                po_obj=po_file.find(msgid)
                if po_obj:
                    po_obj.obsolete=False
                    
            po_file.save()
            po_file.save_as_mofile(f"D:/qr4order_new/qr4v2_django_back/locale/{lang}/LC_MESSAGES/django.mo")

            return JsonResponse({'success': True, 'message': 'Remove Updated Successfully'},http_status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error creating and updating translations'},http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessEntityRegistrations(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    serializer_class = BusinessEntityRegistrationSerializer

    def get(self,request):
        return Response({"message":"get api"},status=status.HTTP_200_OK)

    def post(self,request):
        checking = BusinessEntityRegistrationSerializer(data=request.data)
        if checking.is_valid():
            name = checking.validated_data.get('owner')
            return Response({"message":"done"})
        return Response({"message":checking.errors})
    

class QrSingature(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomAuthentication]
    serializer_class = QrSingatureSerializer

    def get(self,request,id:int):
        print(id,"get")
        return Response({"message":"data"})

    def post(self,request,*args,**kwargs):
        print("data")

        return Response({})

    def put(self,request,id:int):
        print(id,"put")

        return Response({

        })
    
    def patch(self,request,id:int):
        print("patch",id)
        return Response({})

    def delete(self,request,id:int):
        print(id,"delete")
        return Response({})    
