from django.db import models
from django.contrib.auth.models import AbstractUser
from multistore.models import *
# Create your models here.

class UserLevel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class CustomUser(AbstractUser):
    email = models.CharField(max_length=100)
    is_verify = models.BooleanField(default=False)
    identity = models.ForeignKey(UserLevel,null=True,on_delete=models.CASCADE)
    group = models.ManyToManyField("GroupPermission")
    businessentity = models.ForeignKey(
        "multistore.BusinessEntity",on_delete=models.CASCADE,null=True
    )

    def __str__(self) -> str:
        return self.email
    
class Operation(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    name = models.CharField(max_length=100)
    

    def save(self, *args, **kwargs):
        self.name = self.name.replace(' ', '_')
        self.name = self.name.upper()
        super(Permission, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

class StaffPermissions(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name="permisions")
    operation = models.ManyToManyField(Operation)
    bussiness_entity = models.ForeignKey("multistore.BusinessEntity",on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self) -> str:
        return self.name


class GroupPermission(models.Model):
    name = models.CharField(max_length=100,help_text="Group name")
    permision = models.ManyToManyField(Permission)
   

    def __str__(self) -> str:
        return self.name



















    
    
