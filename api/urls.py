from django.urls import include, path
from .views import *

urlpatterns = [
    path('language/<str:lang>/',LanguageDetails.as_view(),name='translations')
]