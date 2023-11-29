from django.contrib import admin
from .models import (
     CustomUser,StaffPermissions,Operation,UserLevel,Permission,
     GroupPermission
)

class BaseReadOnlyAdminMixin:
    def has_add_permission(self, request):
        print(request.user.is_superuser,"user id")
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email','is_verify','identity']
    readonly_fields = ('is_verify','identity')


@admin.register(StaffPermissions)
class StaffPermissionsAdmin(admin.ModelAdmin):
    list_display = ['user','bussiness_entity']


class PermissionAdmin(BaseReadOnlyAdminMixin,admin.ModelAdmin):
    list_display = ['name']
admin.site.register(Permission,PermissionAdmin)



#add permission only super user create
@admin.register(UserLevel)
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ('name',)
    


    
admin.site.register(GroupPermission)