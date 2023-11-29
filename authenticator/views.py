from typing import Any
from django import http
from rest_framework import status
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from rest_framework.views import APIView
from getpass import getpass
from rest_framework.response import Response
import datetime
from .utils import (
    user_registration
)


from jose import jwt


cognito_region = settings.AWS_REGION  
client_id = settings.COGNITO_APP_CLIENT_ID  
user_pool_id = settings.COGNITO_USER_POOL_ID 
cognito_client = boto3.client('cognito-idp', region_name=cognito_region)
# class CustomSignupView(SignupView):
# @csrf_protect


@csrf_exempt
def UserRegistration(request):
    
    try:
        email = request.POST.get('email')
        password = request.POST.get('password')
        establishment_name = request.POST.get('establishment_name')

        user_attributes = [
        {'Name': 'custom:Establishment_Names', 'Value': establishment_name},
        ]

        response = cognito_client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=user_attributes
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

            return JsonResponse({'success': True, 'data': response, 'message': "User Authentication confirmed."})
        except ClientError as e:
            print("UserAuthentication error = ", e)
            return JsonResponse({'success': False, 'message': str(e)})


class ResendConfirmationCode(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            username_or_email = request.POST.get('username_or_email')

            response = cognito_client.resend_confirmation_code(
                ClientId=client_id,
                Username=username_or_email
            )

            print("Confirmation code resent successfully.")

            return JsonResponse({'success': True, 'data': response, 'message': 'Confirmation code resent successfully.'})

        except ClientError as e:
            print(f"Error resending confirmation code: {e}")
            return JsonResponse({'success': False, 'message': str(e)})


class account_recovery(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            email = request.POST.get('email')

            response = cognito_client.forgot_password(
                ClientId=client_id,
                Username=email,
            )

            return JsonResponse({'success': True, 'status_code': status.HTTP_200_OK, 'message': 'Password recovery initiated successfully. Check your email for instructions."'})

        except cognito_client.exceptions.UserNotFoundException:
            print("User not found. Please check the username and try again.")
            return JsonResponse({'success': False, 'message': "User not found. Please check the username and try again."})

        except cognito_client.exceptions.NotAuthorizedException:
            print(
                "User is not authorized to initiate password recovery. Please contact support.")
            return JsonResponse({'success': False, 'data': response, 'message': "User is not authorized to initiate password recovery. Please contact support."})

        except cognito_client.exceptions.LimitExceededException:
            print("Request limit exceeded. Please try again later.")
            return JsonResponse({'success': False, 'data': response, 'message': "Request limit exceeded. Please try again later."})

        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'success': False, 'data': response, 'message': [e]})

class UserDetailsUpdate(APIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):

        responce = cognito_client.admin_update_user_attributes(
                UserPoolId=user_pool_id,
                Username='string',
                UserAttributes=[
                            {
                                'Name': 'string',
                                'Value': 'string'
                            },
                        ],
        )