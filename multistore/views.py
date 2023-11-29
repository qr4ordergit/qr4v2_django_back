from django.shortcuts import render
from rest_framework.views import APIView
from django.utils import translation
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import  JsonResponse
from rest_framework import status as http_status
import polib


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
