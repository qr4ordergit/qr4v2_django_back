
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authenticator.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/',include("restaurant.urls"),name = "api"),
    path('multistore/',include('multistore.urls')),
]
