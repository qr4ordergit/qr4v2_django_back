from django.urls import include, path
from .views import *

urlpatterns = [
    path('profile/creation/', OwnerRegistration.as_view(), name='owner-registration'),
    path('employee/creation/', EmployeeRegistration.as_view(), name='employee-creation'),
    
    path('authentication/', UserAuthentication.as_view(), name='user-authentication'),
    path('resend/confirmation/code/', ResendConfirmationCode.as_view(), name='ResendConfirmationCode'),
    path('login/', UserLogin.as_view(), name='user-login'),
    # path('account/recovery/', account_recovery.as_view(), name='account_recovery'),
    
]