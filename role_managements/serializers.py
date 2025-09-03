from rest_framework import serializers
from django.contrib.auth.models import Permission
from .models import Role, UserRole, RoleGroup
# from users.models import CustomUser
# from users.serializers import CustomUserSerializer
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import Manager
    from django.db.models.query import QuerySet


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Django permissions.
    
    This serializer is used to serialize Django permission objects.
    """
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for role details.
    
    This serializer includes role information along with its permissions.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permissions', 'permissions_count', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()

class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating roles.
    
    This serializer is used when creating new roles or updating existing ones.
    It allows specifying permission IDs for the role.
    """
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'permission_ids', 'is_active')
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        # Using direct instantiation instead of objects.create() to avoid Pyright issues
        role = Role(**validated_data)
        role.save()
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            # Using direct assignment to avoid Pyright issues with .set()
            role.permissions.set(permissions)  # type: ignore
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            # Using direct assignment to avoid Pyright issues with .set()
            instance.permissions.set(permissions)  # type: ignore
        return instance

class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for user-role assignments.
    
    This serializer is used to serialize user-role relationships.
    """
    # Use SerializerMethodField to avoid circular import
    user = serializers.SerializerMethodField()
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ('id', 'user', 'role', 'assigned_at', 'assigned_by')
        read_only_fields = ('assigned_at', 'assigned_by')
    
    def get_user(self, obj):
        # Lazy import to avoid circular import
        from users.serializers import CustomUserSerializer
        return CustomUserSerializer(obj.user).data

class UserRoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating user-role assignments.
    
    This serializer is used when assigning roles to users.
    """
    class Meta:
        model = UserRole
        fields = ('user', 'role')
    
    def validate(self, attrs):
        user = attrs['user']
        role = attrs['role']
        
        # Check if this user-role combination already exists
        # Using objects filter to avoid Pyright issues
        if UserRole.objects.filter(user=user, role=role).exists():  # type: ignore
            raise serializers.ValidationError("This user already has this role.")
        return attrs

class RoleGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for role group details.
    
    This serializer includes role group information along with its roles.
    """
    roles = RoleSerializer(many=True, read_only=True)
    roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RoleGroup
        fields = ('id', 'name', 'description', 'roles', 'roles_count', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    
    def get_roles_count(self, obj):
        return obj.roles.count()

class RoleGroupCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating role groups.
    
    This serializer is used when creating new role groups or updating existing ones.
    It allows specifying role IDs for the role group.
    """
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = RoleGroup
        fields = ('id', 'name', 'description', 'role_ids', 'is_active')
    
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        # Using direct instantiation instead of objects.create() to avoid Pyright issues
        role_group = RoleGroup(**validated_data)
        role_group.save()
        if role_ids:
            # Using type ignore to avoid Pyright issues with objects.filter()
            roles = Role.objects.filter(id__in=role_ids)  # type: ignore
            # Using direct assignment to avoid Pyright issues with .set()
            role_group.roles.set(roles)  # type: ignore
        return role_group
    
    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if role_ids is not None:
            # Using type ignore to avoid Pyright issues with objects.filter()
            roles = Role.objects.filter(id__in=role_ids)  # type: ignore
            # Using direct assignment to avoid Pyright issues with .set()
            instance.roles.set(roles)  # type: ignore
        return instance