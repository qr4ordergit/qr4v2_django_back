from django.shortcuts import render
from rest_framework.views import APIView
from django.utils import translation
from django.utils.translation import gettext as _
from django.conf import settings
from django.http import HttpResponse, JsonResponse


class LanguageDetails(APIView):

    def get(self,request,lang):
        translation.activate(lang)

        translations = {}

        for i in range(1111, 1123):
            translations[str(i)] = _(str(i))
        
        return JsonResponse(translations)

