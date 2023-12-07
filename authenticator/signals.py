from .models import Permission
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete


# @receiver(post_save, sender=Permission) 
# def create_premission(sender, instance, created, **kwargs):
#     if created:
#         permission_name = instance.name
#         Permission.objects.bulk_create(
#             [
#             Permission(name=f'{permission_name}_ADD'),
#             Permission(name=f'{permission_name}_EDIT'),
#             Permission(name=f'{permission_name}_VIEW'),
#             Permission(name=f'{permission_name}_DELETE'),
#             ]
#         )
#         #delete previous one
#         try:
#             Permission.objects.get(id=instance.id).delete()
#         except:
#             pass



