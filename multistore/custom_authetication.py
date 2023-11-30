from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from authenticator.token_decoder import (
    verify_cognito_access_token
)
from rest_framework.response import Response

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization',None)
        if header is None:
            raise AuthenticationFailed("header is missing")
        
        return



        
        