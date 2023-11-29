
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authenticator.urls')),
    path('accounts/', include('allauth.urls')),
    path('multistore/',include('multistore.urls')),
]
