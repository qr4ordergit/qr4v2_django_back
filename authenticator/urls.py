from django.urls import include, path
from .views import *
from .views2 import PermissionView

urlpatterns = [
    path('refresh/token/', silent_token_refresh),
    path('profile/creation/', OwnerRegistration.as_view(), name='owner-registration'),
    path('employee/creation/', EmployeeRegistration.as_view(), name='employee-creation'),    
    path('employee/updation/', UserDetailsUpdate.as_view(), name='employee-updation'),    
    path('authentication/', UserAuthentication.as_view(), name='user-authentication'),
    path('resend/confirmation/code/', ResendConfirmationCode.as_view(), name='resend-confirmation'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('staff/login/', StaffLogin.as_view(), name='staff-login'),
    path('forgot/password/', AccountRecovery.as_view(), name='forgot-password'),
    path('update/password/', UserPasswordUpdate.as_view(), name='user-forgot-password'),
    path('delete/user/', DeleteUser.as_view(), name='delete-user'),
    
    path('api/permission',PermissionView.as_view(),name="permission")
]