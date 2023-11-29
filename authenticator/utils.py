#saved user
from .models import CustomUser

def user_registration(email_data:str,password_hash:str,user_level:object):
    custom_user = CustomUser(
        email = email_data,
        username = email_data
    )
    custom_user.set_password(password_hash)
    custom_user.identity = user_level
    custom_user.save()
    return True


def check_user_verify(email:str):
    user = CustomUser.objects.get(email=email)
    if user.is_verify:
        return True
    else:
        return False
    
