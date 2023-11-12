from django.urls import path
from authenticator import views

urlpatterns = [

    path('signup/', views.UserRegistration, name='UserRegistration'),
    path('authentication/', views.UserAuthentication, name='UserAuthentication'),
    path('login/', views.UserLogin, name='UserLogin'),
    path('account/recovery/', views.account_recovery, name='account_recovery'),

]