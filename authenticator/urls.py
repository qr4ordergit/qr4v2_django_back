from django.urls import include, path
from authenticator import views

urlpatterns = [
    path('signup/', views.UserRegistration, name='UserRegistration'),
    path('authentication/', views.UserAuthentication, name='UserAuthentication'),
    path('resend/confirmation/code/', views.ResendConfirmationCode, name='ResendConfirmationCode'),
    path('login/', views.UserLogin, name='UserLogin'),
    path('account/recovery/', views.account_recovery, name='account_recovery'),
    
]