from django.urls import include, path
from .views import *

urlpatterns = [
    path('language/<str:lang>/',LanguageDetails.as_view(),name='translations'),
    path('language/set/<str:lang>/',LanguageCrud.as_view(),name='translations_cr')

]