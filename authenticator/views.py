from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from allauth.account.views import LoginView, SignupView, LogoutView
from django.conf import settings
import boto3
import botocore
from getpass import getpass
import datetime


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
        print("User signup confirmed.")

        return JsonResponse({'success': True, 'data': response,'message':"User Authentication confirmed."})
    except botocore.exceptions.ClientError as e:
        print("UserAuthentication error = ",e)
        return JsonResponse({'success': False, })

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




import requests

def get_cognito_public_keys():
    # Retrieve Cognito public keys
    jwks_url = 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Ggw6POqGJ/.well-known/jwks.json'
    response = requests.get(jwks_url)
    jwks = response.json()['keys']
    return {key['kid']: key for key in jwks}

def verify_cognito_access_token(access_token, public_keys):
    try:
        # Decode and verify the access token
        header = jwt.get_unverified_header(access_token)
        kid = header['kid']
        key = public_keys[kid]

        decoded_token = jwt.decode(access_token, key, algorithms=['RS256'], audience='your-client-id')
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.JWTClaimsError:
        print("Invalid token claims.")
        return None
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None



      
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
            access_token = response['AuthenticationResult']['AccessToken']

            # Verify the access token using python-jose
            public_keys = get_cognito_public_keys()
            decoded_token = verify_cognito_access_token(access_token, public_keys)

            if decoded_token:
                # Access token is valid, perform additional actions
                user_data = {'sub': decoded_token.get('sub')}  # Include additional user data as needed
                data= {'access_token': access_token, 'user_data': user_data}
                return JsonResponse({'success': True, 'message': 'Authenticated User.'})
            else:
                return JsonResponse({'success': False, 'message': 'Access token verification failed.'})
        else:
            return JsonResponse({'success': False, 'message': 'User Not Authenticated.'})
    
    except botocore.exceptions.ClientError as e:
        print(f"Authentication failed: {e}")
        return JsonResponse({'success': False, 'message': 'Error during authentication.'})       
    
    
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
    


    