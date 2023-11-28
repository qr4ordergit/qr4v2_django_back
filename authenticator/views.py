from typing import Any
from django import http
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from rest_framework.views import APIView
from getpass import getpass
import datetime

from .token_decoder import get_cognito_public_keys, verify_cognito_access_token


cognito_region = settings.AWS_REGION  
client_id = settings.COGNITO_APP_CLIENT_ID  
user_pool_id = settings.COGNITO_USER_POOL_ID 
cognito_client = boto3.client('cognito-idp', region_name=cognito_region)


class OwnerRegistration(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self,request):

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_attributes = [
            # {'Name': 'custom:Establishment_Names', 'Value': establishment_name},
            {'Name': 'email', 'Value': email},
            ]

            response = cognito_client.sign_up(
                ClientId=client_id,
                Username=email,
                Password=password,
                UserAttributes=user_attributes
            )

            add_owner_to_group = cognito_client.admin_add_user_to_group(
                UserPoolId = user_pool_id,
                Username = email,
                GroupName = 'Owner',
                )

            
            return JsonResponse({'success': True, 'data': response, 'message':'User signup successful. Confirm signup with the code sent to your email.'})
        except cognito_client.exceptions.UsernameExistsException:
            return JsonResponse({'success': False, 'message': 'Username Already Exists.'})
        except cognito_client.exceptions.InvalidPasswordException:
            return JsonResponse({'success': False,'message': 'Invalid Password.'})
        except ClientError as e:
            print(f"User signup failed =>> {e}")
            # delete_user = cognito_client.admin_delete_user(
            #                 UserPoolId=user_pool_id,
            #                 Username=email )
            return JsonResponse({'success': False, 'data': str(e), 'message': 'User creation failed. Please check your input and try again.'})
    
class EmployeeRegistration(APIView): 

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            restuarent_name = request.POST.get('restuarent_name')
            password = request.POST.get('password')
            group_name = 'Staff'
            # group_name = request.POST.get('group_name')
            role = request.POST.get('role')
            placeholder_email = f'{role}@example.com'
    
            password = f'Qr4oreder@{password}'
            user_attributes = [
            # {'Name': 'custom:Establishment_Names', 'Value': ''},
            # {'Name': 'custom:Restuarent_Name', 'Value': restuarent_name},
            {'Name': 'email', 'Value':placeholder_email},
            {'Name': 'email_verified', 'Value': 'True'},               
            ]

            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=role,
                TemporaryPassword=password,
                UserAttributes=user_attributes,
                ForceAliasCreation=False,
            )
            
            user_response=response['ResponseMetadata']['HTTPStatusCode']

            add_user_to_group = cognito_client.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username= role,
                GroupName=group_name,
                ) 
            group_responce = add_user_to_group['ResponseMetadata']['HTTPStatusCode']

            if group_responce == 200 and user_response == 200:
                return JsonResponse({'success': True, 'data': response, "message":"User Createtion successful."})
            
        except ClientError as e:
            print(f"User signup failed =>> {e}")
            return JsonResponse({'success': False, 'data': str(e), 'message': 'User creation failed. Please check your input and try again.'})
            

class UserLogin(APIView):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            username_or_email = request.POST.get('username_or_email')
            password = request.POST.get('password')

            if '@'not in username_or_email:
                password = f'Qr4oreder@{password}'

            response = cognito_client.initiate_auth(
                ClientId=client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username_or_email,
                    'PASSWORD': password 
                }
            )

            if 'ChallengeName' in response and response['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                # This code is essential for authenticating and validating users created by the owner.
                session = response['Session']
                staff_response = cognito_client.respond_to_auth_challenge(
                ClientId=client_id,
                ChallengeName='NEW_PASSWORD_REQUIRED',
                ChallengeResponses={
                    'USERNAME': username_or_email,
                    'NEW_PASSWORD': password
                },Session=session)

                response = staff_response

            if 'AuthenticationResult' in response:
                access_token = response['AuthenticationResult']['AccessToken']
                refresh_token = response['AuthenticationResult']['RefreshToken']
                # Verifing the access token using python-jose
                public_keys = get_cognito_public_keys()
                decoded_token = verify_cognito_access_token(access_token, public_keys)

                if decoded_token:
                    # Access token is valid, perform additional actions
                    user_data = {'sub': decoded_token.get('sub')}  # Include additional user data as needed
                    data= {'access_token': access_token, 'refresh_token':refresh_token,'user_data': user_data}
                    return JsonResponse({'success': True, 'data': data,'message': 'Authenticated User.'})
                else:
                    return JsonResponse({'success': False, 'message': 'Access token verification failed.'})
        except cognito_client.exceptions.UserNotConfirmedException:
            return JsonResponse({'success': False, 'verified':False, 'message': 'User not Verified.'})
        except cognito_client.exceptions.NotAuthorizedException:
            return JsonResponse({'success': False, 'message': 'Incorrect username or password.'})
        except ClientError as e:
            print(f"Authentication failed: {e}")
            return JsonResponse({'success': False, 'message': str(e)})    

class UserAuthentication(APIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            email = request.POST.get('email')
            confirmation_code = request.POST.get('code')

            response = cognito_client.confirm_sign_up(
                ClientId=client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )


            return JsonResponse({'success': True, 'data': response,'message':"User Authentication confirmed."})
        except ClientError as e:
            print("UserAuthentication error = ",e)
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

            return JsonResponse({'success': True, 'data': response, 'message':'Confirmation code resent successfully.'})
        
        except ClientError as e:
            print(f"Error resending confirmation code: {e}")
            return JsonResponse({'success': False, 'message': str(e)})

  
   
    
    
@csrf_exempt    
def account_recovery(request):
    try:
        email = request.POST.get('email')

        response = cognito_client.forgot_password(
            ClientId=client_id,
            Username=email,
        )

        return JsonResponse({'success': True, 'message': 'Password recovery initiated successfully. Check your email for instructions."'})
    
    except cognito_client.exceptions.UserNotFoundException:
        print("User not found. Please check the username and try again.")
        return JsonResponse({'success': True,'message':"User not found. Please check the username and try again."})
    
    except cognito_client.exceptions.NotAuthorizedException:
        print("User is not authorized to initiate password recovery. Please contact support.")
        return JsonResponse({'success': True, 'data': response,'message':"User is not authorized to initiate password recovery. Please contact support."})
    
    except cognito_client.exceptions.LimitExceededException:
        print("Request limit exceeded. Please try again later.")
        return JsonResponse({'success': True, 'data': response,'message':"Request limit exceeded. Please try again later."})
    
    except Exception as e:
        print(f"An error occurred: {e}")  
        return JsonResponse({'success': True, 'data': response,'message':[e]})
    


    