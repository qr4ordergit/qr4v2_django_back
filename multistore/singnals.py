from .models import BusinessEntity
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from authenticator.models import Permission
#create common permision when BusinessEntity is created.




