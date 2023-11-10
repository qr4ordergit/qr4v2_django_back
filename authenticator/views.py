from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from allauth.account.views import LoginView, SignupView, LogoutView
from django.conf import settings
import boto3
import botocore
from getpass import getpass

cognito_region = settings.AWS_REGION  
client_id = settings.COGNITO_APP_CLIENT_ID  
cognito_client = boto3.client('cognito-idp', region_name=cognito_region)
# class CustomSignupView(SignupView):
# @csrf_protect
@csrf_exempt
def UserRegistration(request):
    
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')

        response = cognito_client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password
        )
        print("User signup successful. Confirm signup with the code sent to your email.")
        
        return JsonResponse({'success': True, 'data': response})
    
    except botocore.exceptions.ClientError as e:
        print(f"User signup failed =>> {e}")
        message = {e}
        return JsonResponse({'success': False})

@csrf_exempt
def UserAuthentication(request):
    try:
        email = request.POST.get('email')
        confirmation_code = request.POST.get('code')

        response = cognito_client.confirm_sign_up(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=confirmation_code
        )
        print("User signup confirmed.")

        return JsonResponse({'success': True, 'data': response,'message':"User Authentication confirmed."})
    except botocore.exceptions.ClientError as e:
        message = e
        return JsonResponse({'success': False})


@csrf_exempt
def UserLogin(request):
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')

        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        if 'AuthenticationResult' in response:
            print("User authentication successful.")
            data = response['AuthenticationResult']['AccessToken']
            return JsonResponse({'success': True, 'data': data})
        else:
            return JsonResponse({'success': True, 'message': 'User Not Authenticated.'})
    except botocore.exceptions.ClientError as e:
        print(f"Authentication failed: {e}")        

        return JsonResponse({'success': False})         