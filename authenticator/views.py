from rest_framework import status
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
from .models import UserLevel
from multistore.models import BusinessEntity

from .token_decoder import get_cognito_public_keys, verify_cognito_access_token


cognito_region = settings.AWS_REGION
client_id = settings.COGNITO_APP_CLIENT_ID
user_pool_id = settings.COGNITO_USER_POOL_ID
cognito_client = boto3.client('cognito-idp', region_name=cognito_region)


class OwnerRegistration(APIView):

    def post(self, request):

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_attributes = [
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
            
            try:
                owner, created = UserLevel.objects.get_or_create(name='OWNER')
                print(owner,"user level saved")
                user_registration(email,password,owner)
            except Exception as e:
                print("Failed to Registerations in Django User Model")
           
            return JsonResponse({'success': True, 'status_code': status.HTTP_200_OK, 'data': response, 'message': 'User signup successful. Confirm signup with the code sent to your email.'})
        except cognito_client.exceptions.UsernameExistsException:
            return Response({'success': False, 'message': 'Username Already Exists.'})
        except cognito_client.exceptions.InvalidPasswordException:
            return JsonResponse({'success': False,'message': 'Invalid Password.'})
        except ClientError as e:
            print(f"User signup failed =>> {e}")
            # delete_user = cognito_client.admin_delete_user(
            #                 UserPoolId=user_pool_id,
            #                 Username=email )
            return JsonResponse({'success': False, 'data': str(e), 'message': 'User creation failed. Please check your input and try again.'})
    
class EmployeeRegistration(APIView): 

    def check_user_level_exits(self,role):
        try:
            user_level = UserLevel.objects.get(name=role)
            return user_level
        except:
            return False
        
    def businessentity_data(self,id:int):
        try:
            object = BusinessEntity.objects.get(id=id)
            return object
        except:
            return None
    

    def post(self, request):
        try:
            user_name = request.POST.get('username')
            role = request.POST.get('role')
            password = request.POST.get('password')
            businessentity = request.POST.get('businessentity')
            placeholder_email = f'{user_name}@example.com'
            password = f'Qr4oreder@{password}'

            check_business = self.businessentity_data(businessentity)
            if check_business == None:
                return Response({
                    "message":"businessentity not exits"
                })

            user_level_check = self.check_user_level_exits(role)
            if user_level_check == False:
                return Response({
                    "message":"given role not exits"
                })
            
            user_attributes = [
                {'Name': 'email', 'Value': placeholder_email},
                {'Name': 'email_verified', 'Value': 'True'},
            ]

            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=user_name,
                TemporaryPassword=password,
                UserAttributes=user_attributes,
                ForceAliasCreation=False,
            )

            user_response = response['ResponseMetadata']['HTTPStatusCode']

            add_user_to_group = cognito_client.admin_add_user_to_group(
                UserPoolId=user_pool_id,
                Username=role,
                GroupName='Staff',
            )

            group_responce = add_user_to_group['ResponseMetadata']['HTTPStatusCode']

            if group_responce == 200 and user_response == 200:
                
                user_registration(placeholder_email,password,user_level_check)

                return Response({'success': True, 'status_code': status.HTTP_200_OK, 'data': response, "message": "User Createtion successful."})

        except cognito_client.exceptions.UsernameExistsException:
            return Response({'success': False, 'message': 'Username Already Exists.'})
        except cognito_client.exceptions.InvalidPasswordException:
            return Response({'success': False, 'message': 'Invalid Password.'})
        except ClientError as e:
            print(f"User signup failed =>> {e}")
            return Response({'success': False, 'message': 'User creation failed. Please check your input and try again.'})


class UserLogin(APIView):

    def post(self, request):
        try:
            username_or_email = request.POST.get('username_or_email')
            password = request.POST.get('password')

            if username_or_email and password:

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
                        }, Session=session)

                    response = staff_response

                if 'AuthenticationResult' in response:
                    access_token = response['AuthenticationResult']['AccessToken']
                    refresh_token = response['AuthenticationResult']['RefreshToken']
                    # Verifing the access token using python-jose
                    public_keys = get_cognito_public_keys()
                    decoded_token = verify_cognito_access_token(
                        access_token, public_keys)

                    if decoded_token:
                        if  username_or_email == 'test': 
                            user_type = 'Manager' 
                        elif username_or_email == 'test2':
                            user_type = 'Waiter'
                        else:
                            user_type = 'Owner'

                        user_data = {'sub': decoded_token.get('sub'), 
                                    'user_type': user_type}
                        
                        data = {'access_token': access_token,
                                'refresh_token': refresh_token, 'user_data': user_data}
                        return JsonResponse({'success': True, 'status_code': status.HTTP_200_OK, 'data': data, 'message': 'Authenticated User.'})
                    else:
                        return Response({'success': False, 'message': 'Access token verification failed.'})
            
            return Response({'success': False, 'message': 'Incorrect username or password.'})    
        
        except cognito_client.exceptions.UserNotConfirmedException:
            return Response({'success': False, 'verified': False, 'message': 'User not Verified.'})
        except cognito_client.exceptions.NotAuthorizedException:
            return Response({'success': False, 'message': 'Incorrect username or password.'})
        except ClientError as e:
            print(f"Authentication failed: {e}")
            return Response({'success': False, 'message': str(e)})


class UserAuthentication(APIView):

    def post(self, request):
        try:
            email = request.POST.get('email')
            confirmation_code = request.POST.get('code')

            response = cognito_client.confirm_sign_up(
                ClientId=client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )

            return JsonResponse({'success': True, 'data': response, 'message': "User Authentication confirmed."})
        except cognito_client.exceptions.ExpiredCodeException:
            return Response({'success': False, 'message': 'Invalid code provided, please request a code again.'})
        except ClientError as e:
            print("UserAuthentication error = ", e)
            return Response({'success': False, 'message': str(e)})


class ResendConfirmationCode(APIView):

    def post(self, request):
        try:
            username_or_email = request.POST.get('username_or_email')

            response = cognito_client.resend_confirmation_code(
                ClientId=client_id,
                Username=username_or_email
            )

            return Response({'success': True, 'message': 'Confirmation code resent successfully.'})
        
        except cognito_client.exceptions.UserNotFoundException:
            return Response({'success': False,'status_code': status.HTTP_404_NOT_FOUND ,'message': "User not found. Please check the username and try again."})
        except ClientError as e:
            print(f"Error resending confirmation code: {e}")
            return Response({'success': False, 'message': str(e)})


class account_recovery(APIView):

    def post(self, request):
        try:
            email = request.POST.get('email')

            response = cognito_client.forgot_password(
                ClientId=client_id,
                Username=email,
            )

            return Response({'success': True, 'status_code': status.HTTP_200_OK, 'message': 'Password recovery initiated successfully. Check your email for instructions."'})

        except cognito_client.exceptions.UserNotFoundException:
            return Response({'success': False,'status_code': status.HTTP_404_NOT_FOUND ,'message': "User not found. Please check the username and try again."})
        except cognito_client.exceptions.NotAuthorizedException:
            return Response({'success': False, 'status_code': status.HTTP_401_UNAUTHORIZED, 'message': "User is not authorized to initiate password recovery. Please contact support."})
        except cognito_client.exceptions.LimitExceededException:
            return Response({'success': False, 'status_code': status.HTTP_503_SERVICE_UNAVAILABLE, 'message': "Request limit exceeded. Please try again later."})
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'success': False, 'data': response, 'message': [e]})

class UserDetailsUpdate(APIView):
    
    def post(self, request):
        try:
            current_username = request.POST.get('current_username')
            new_username = request.POST.get('new_username')

            if current_username and new_username:
                user_attributes = [
                    {'Name': 'email', 'Value': f'{new_username}@example.com'},
                    {'Name': 'preferred_username', 'Value': new_username},
                ]

                response = cognito_client.admin_update_user_attributes(
                    UserPoolId=user_pool_id,
                    Username=current_username,
                    UserAttributes=user_attributes
                )

                return Response({'success': True, 'message': "User Details Updated Successfully."})
            
            return Response({'success': False, 'status_code': status.HTTP_400_BAD_REQUEST ,'message': "Request Failed. Please try again later."})
        except cognito_client.exceptions.InvalidParameterException:
            return Response({'success': False, 'message': f"Invalid Parameter, Please try again."})
        except cognito_client.exceptions.UserNotFoundException:
            return Response({'success': False, 'status_code': status.HTTP_404_NOT_FOUND,'message': f"User Not Found, Please try again."})
        # except cognito_client.exceptions.LimitExceededException:
        #     return Response({'success': False, 'status_code': status.HTTP_503_SERVICE_UNAVAILABLE, 'message': f"Internal Server Error, Please try again."})
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'success': False, 'message': str(e)})
