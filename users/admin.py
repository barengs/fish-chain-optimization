from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OwnerProfile, CaptainProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_owner', 'get_owner_name', 'id_number', 'company_name')
    search_fields = ('first_name', 'last_name', 'id_number', 'company_name', 'company_registration_number')
    list_filter = ('type_owner',)
    
    @admin.display(description='Owner Name')
    def get_owner_name(self, obj):
        if obj.type_owner == 'individual' and obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.type_owner == 'company' and obj.company_name:
            return obj.company_name
        return "N/A"

class CaptainProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'license_number')
    search_fields = ('first_name', 'last_name', 'license_number')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OwnerProfile, OwnerProfileAdmin)
admin.site.register(CaptainProfile, CaptainProfileAdmin)