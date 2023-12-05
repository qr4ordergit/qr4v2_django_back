from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from authenticator.token_decoder import (
    verify_cognito_access_token,get_cognito_public_keys
)
from rest_framework.response import Response
from authenticator.models import CustomUser


def idetify_user(name_or_email):
    try:
        user = CustomUser.objects.get(email=name_or_email)
    except Exception as e:
        user = None
    try:
        user = CustomUser.objects.get(username=name_or_email)
    except Exception as e:
        user = None
    return user

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization',None)
        if header is None:
            return AuthenticationFailed("header is missing")
        try:
            public_key = get_cognito_public_keys()
            verify = verify_cognito_access_token(header,public_key)
            username_or_email = verify['username']

        except Exception as e:
            return AuthenticationFailed(e)
            
        finally:
            user = idetify_user(username_or_email)

        return (user,None)