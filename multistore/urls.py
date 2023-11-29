from django.urls import include, path
from .views import *
from . multistore_api import Registrations

urlpatterns = [
    path('language/<str:lang>/',LanguageDetails.as_view(),name='translations'),
    path('language/set/<str:lang>/',LanguageCrud.as_view(),name='translations_cr'),
    path('registratoins/',Registrations.as_view(),name="registrations"),

]