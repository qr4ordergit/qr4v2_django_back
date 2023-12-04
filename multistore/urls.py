from django.urls import include, path
from .views import *

# url = 'api'

urlpatterns = [
    path('language/<str:lang>/',LanguageDetails.as_view(),name='translations'),
    path('language/set/<str:lang>/',LanguageCrud.as_view(),name='translations_cr'),
    path('businessentity-registratoins/',BusinessEntityRegistrations.as_view(),name="registrations"),
    path('businessentity-details/<int:owner_id>/',BusinessEntityRegistrations.as_view(),name="registrations"),
    path('qrsingature/',QrSingature.as_view(),name="qrsingature"),
    path('qrsingature/<int:id>/',QrSingature.as_view(),name="qr_singature_update")
]