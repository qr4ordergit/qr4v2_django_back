from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    email = models.CharField(max_length=100)
    is_verify = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.email
    
    
