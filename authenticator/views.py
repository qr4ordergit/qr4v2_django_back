from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from allauth.account.views import LoginView, SignupView, LogoutView
from django.conf import settings
import boto3
import botocore
from getpass import getpass
import datetime

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

        user_details = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=email
        )
        print("user_details",user_details['Username'])
        print("user_details",user_details)
   

        group_name = 'Owner'  
        if 'Username' in user_details:
            username = user_details['Username']
            
            if any(attr['Name'] == 'email_verified' and attr['Value'] == 'true' for attr in user_details['UserAttributes']) and user_details['UserStatus'] == 'CONFIRMED':
                cognito_client.admin_add_user_to_group(
                    UserPoolId=user_pool_id,
                    Username=username,
                    GroupName=group_name
                )
        

        return JsonResponse({'success': True, 'message':"User Authentication confirmed."})
    except (
                cognito_client.exceptions.InvalidParameterException,
                cognito_client.exceptions.ResourceNotFoundException,
                cognito_client.exceptions.TooManyRequestsException,
                cognito_client.exceptions.NotAuthorizedException,
                cognito_client.exceptions.UserNotFoundException,
                cognito_client.exceptions.InternalErrorException,
                cognito_client.exceptions.LimitExceededException,
            ) as e:
        print(e)
        return JsonResponse({'success': False})

@csrf_exempt
def ResendConfirmationCode(request):
    try:
        username_or_email = request.POST.get('username_or_email')

        response = cognito_client.resend_confirmation_code(
            ClientId=client_id,
            Username=username_or_email
        )

        print("Confirmation code resent successfully.")

        return JsonResponse({'success': True, 'data': response, 'message':'Confirmation code resent successfully.'})
    
    except botocore.exceptions.ClientError as e:
        print(f"Error resending confirmation code: {e}")
        return JsonResponse({'success': False, 'message': str(e)})

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

        user_group_details = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=email
        )

        if 'Username' in user_group_details:
            username = user_group_details['Username']

            # Get the groups for the user
            groups_response = cognito_client.admin_list_groups_for_user(
                Username=username,
                UserPoolId=user_pool_id
            )

            user_groups = groups_response['Groups']
            group_names = [group['GroupName'] for group in user_groups]

        print("group_names",group_names)
        if 'AuthenticationResult' in response:
            access_token = response['AuthenticationResult']['AccessToken']
            expires_in_seconds  = response['AuthenticationResult']['ExpiresIn']

            expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in_seconds)
            print(f"Access token expiration time (in seconds): {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}")

            user_info = cognito_client.get_user(
                AccessToken=access_token
            )

            # This is to check email verified or not
            email_verified = next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'email_verified'), 'N/A')

            user_attributes = user_info.get('UserAttributes', []) # this is to fetch all user_attributes
            # print(f"User attributes: {user_attributes}")
            # print(f"User email_verified: {email_verified}")

            user_attributes = user_info['UserAttributes']

            user_data = {}
            for attribute in user_attributes:
                user_data[attribute['Name']] = attribute['Value']

            return JsonResponse({'success': True, 'data': access_token})
        else:
            return JsonResponse({'success': True, 'message': 'User Not Authenticated.'})
    except botocore.exceptions.ClientError as e:
        print(f"Authentication failed: {e}")        

        return JsonResponse({'success': False})         
    
    
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
    


    