from jose import jwt
import requests
from django.conf import settings
cognito_region = settings.AWS_REGION 
user_pool_id = settings.COGNITO_USER_POOL_ID
client_id = settings.COGNITO_APP_CLIENT_ID 

def get_cognito_public_keys():
    # Retrieve Cognito public keys
    # jwks_url = 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Ggw6POqGJ/.well-known/jwks.json'
    jwks_url = f'https://cognito-idp.{cognito_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
    response = requests.get(jwks_url)
    jwks = response.json()['keys']
    return {key['kid']: key for key in jwks}


def verify_cognito_access_token(access_token, public_keys):
    try:
        # Decode and verify the access token
        header = jwt.get_unverified_header(access_token)
        kid = header['kid']
        key = public_keys[kid]
        
        if key:
            decoded_token = jwt.decode(access_token, key, algorithms=['RS256'], audience=client_id)
            return decoded_token
        else:
            raise jwt.JWTError("Invalid key ID")
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired.")
    except jwt.JWTClaimsError:
        raise jwt.JWTClaimsError("Invalid token claims.")
    except jwt.JWTError as e:
        raise jwt.JWTError(f"Token verification failed: {e}")