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
from datetime import datetime, timedelta
from .utils import (
    user_registration
)
from .models import UserLevel,CustomUser
from multistore.models import Outlet
from .token_decoder import get_cognito_public_keys, verify_cognito_access_token


cognito_region = settings.AWS_REGION
client_id = settings.COGNITO_APP_CLIENT_ID
user_pool_id = settings.COGNITO_USER_POOL_ID
cognito_client = boto3.client('cognito-idp', region_name=cognito_region)


def silent_token_refresh(refresh_token):

    try:
        response = cognito_client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )

        if 'AuthenticationResult' in response:              
                access_token = response['AuthenticationResult']['AccessToken']
                expires_in_seconds = response['AuthenticationResult'].get('ExpiresIn')
                new_refresh_token = response['AuthenticationResult'].get('RefreshToken')
                expiration_time = datetime.now() + timedelta(seconds=expires_in_seconds)

                data ={
                    'access_token': access_token,
                    'refresh_token': new_refresh_token,
                    'expires_in': expires_in_seconds,
                    'expiration_time': expiration_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                return JsonResponse({'success': True, 'data': data})
    except cognito_client.exceptions.UserNotFoundException: 
        return Response({'success': False,'status_code': status.HTTP_404_NOT_FOUND ,'message': "User not found."})
    except ClientError as e:
        return Response({'success': False, 'data':str(e)})
    
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
        
    def get_outlet_code(self,code):
        try:
            object = Outlet.objects.get(outlet_code=code)
            return object
        except:
            return None
    

    def post(self, request):
        try:
            username = request.POST.get('username')
            role = request.POST.get('role')
            password = request.POST.get('password')
            outletcode = request.POST.get('outletcode')
            
            placeholder_email = f'{username}@example.com'
            password = f'Qr4order@{password}'

            outlet_obj = self.get_outlet_code(outletcode)
            if outlet_obj == None:
                return Response({
                    "message":"outlet not exits"
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
                Username=username,
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

    def get_user(self,usrename):
        try:
            user = CustomUser.objects.get(username=usrename).id
        except Exception as e:
            print(e,"error")
            user = None
        return user

    def post(self, request):
        try:
            username_or_email = request.POST.get('username_or_email')
            password = request.POST.get('password')

            if username_or_email and password:

                if '@'not in username_or_email:
                    password = f'Qr4order@{password}'
                
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
                    expires_in_seconds = response['AuthenticationResult'].get('ExpiresIn')

                    expiration_time = datetime.now() + timedelta(seconds=expires_in_seconds)
                    silent_token_refresh(refresh_token)
                    get_user_details = self.get_user(username_or_email)
                    
                    
                    if  username_or_email == 'test': 
                        user_type = 'Manager' 
                    elif username_or_email == 'test2':
                        user_type = 'Waiter'
                    else:
                        user_type = 'Owner'
                    
                    user_data = {
                                }
                    print("user_data",user_data)

                    data = {'expiration_time':expiration_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'user_id':get_user_details,
                            'user_type':user_type,
                            # 'user_identity': str(get_user_details.identity), 
                            'email':username_or_email,                         
                            'access_token': access_token,
                            'refresh_token': refresh_token}
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



class AccountRecovery(APIView):

    def get(self, request):
        username = request.POST.get('username')
        code = request.POST.get('code')
        password = request.POST.get('password')
        try:
            if '@' in username:
                responce = cognito_client.forgot_password(
                    ClientId = client_id,
                    Username = username,
                )
                return Response({'success': True,'data':responce, 'message': 'Confirm with the code sent to your email.'})
  
            if code:
                responce = cognito_client.confirm_forgot_password(
                    ClientId = client_id,
                    Username = username,
                    ConfirmationCode = code,
                    Password = password,
                )
                return Response({'success': True,'data':responce, 'message': 'Password Changed.'})
        
        except cognito_client.exceptions.NotAuthorizedException:
            return Response({'success': False, 'status_code': status.HTTP_401_UNAUTHORIZED, 'message': "User is not authorized to initiate password recovery. Please contact support."})
        except cognito_client.exceptions.LimitExceededException:
            return Response({'success': False, 'status_code': status.HTTP_503_SERVICE_UNAVAILABLE, 'message': f"Internal Server Error, Please try again."})
        except cognito_client.exceptions.UserNotFoundException:
            return Response({'success': False, 'status_code': status.HTTP_404_NOT_FOUND,'message': f"User Not Found, Please try again."})
        except cognito_client.exceptions as e:
            print(f"An error occurred: {e}")
            return Response({'success': False, 'message': str(e)})
        

class UserPasswordUpdate(APIView):

    def post(self, request):

        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        try:
            password = f'Qr4order@{old_password}'

            access_token = cognito_client.initiate_auth(
                    ClientId=client_id,
                    AuthFlow='USER_PASSWORD_AUTH',
                    AuthParameters={
                        'USERNAME': username,
                        'PASSWORD': password
                    }
                )
            
            if 'AuthenticationResult' in access_token:
                    new_password = f'Qr4order@{new_password}'
                    access_token = access_token['AuthenticationResult']['AccessToken']
                    responce = cognito_client.change_password(
                        PreviousPassword = password,
                        ProposedPassword = new_password,    
                        AccessToken = access_token,
                    )
                    return JsonResponse({'success': True,'status_code': status.HTTP_200_OK, 'data':responce, 'message': 'Password Changed.'})
            return Response({'success': False,  'status_code': status.HTTP_400_BAD_REQUEST ,'message': 'Parameters Mismatch.'})
        except cognito_client.exceptions.NotAuthorizedException:
            return Response({'success': False, 'status_code': status.HTTP_401_UNAUTHORIZED, 'message': "User is not authorized to initiate password recovery. Please contact support."}) 
        

class DeleteUser(APIView):

    def post(self, request):
        username = request.POST.get('username')
        try:
            delete_user = cognito_client.admin_delete_user(
                                UserPoolId=user_pool_id,
                                Username=username 
                                )
            print("User deleted",delete_user)
            return JsonResponse({'success': True,'status_code': status.HTTP_200_OK, 'message': f'User {username} Deleted.'})
        
        except cognito_client.exceptions.NotAuthorizedException:
            return Response({'success': False, 'status_code': status.HTTP_401_UNAUTHORIZED, 'message': "User is not authorized to initiate password recovery. Please contact support."}) 
        except cognito_client.exceptions as e:
            print(f"An error occurred: {e}")
            return Response({'success': False, 'message': str(e)})

