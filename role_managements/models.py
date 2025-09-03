from django.db import models
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    """
    Custom Role model that extends Django's built-in permission system.
    
    This model allows dynamic role creation and management, with the ability
    to assign specific permissions to each role.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Role Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    permissions = models.ManyToManyField(
        Permission, 
        blank=True,
        verbose_name=_("Permissions"),
        help_text=_("Specific permissions for this role.")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ['name']
    
    def __str__(self) -> str:
        return str(self.name)
    
    def add_permission(self, permission) -> None:
        """Add a permission to this role"""
        self.permissions.add(permission)  # type: ignore
    
    def remove_permission(self, permission) -> None:
        """Remove a permission from this role"""
        self.permissions.remove(permission)  # type: ignore
    
    def has_permission(self, permission) -> bool:
        """Check if this role has a specific permission"""
        return self.permissions.filter(pk=permission.pk).exists()  # type: ignore

class UserRole(models.Model):
    """
    Model to associate users with roles.
    
    This model creates a many-to-many relationship between users and roles,
    allowing users to have multiple roles. It also tracks who assigned the role
    and when it was assigned.
    """
    # Use string reference to avoid circular import
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_("User")
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_("Role")
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Assigned At"))
    # Use string reference to avoid circular import
    assigned_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name=_("Assigned By")
    )
    
    class Meta:
        unique_together = ('user', 'role')
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.role.name}"  # type: ignore

class RoleGroup(models.Model):
    """
    Model to group roles together for easier management.
    
    This model allows creating groups of roles that can be managed together,
    making it easier to assign multiple roles to users or manage permissions
    for similar user types.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Group Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    roles = models.ManyToManyField(
        Role, 
        blank=True,
        verbose_name=_("Roles"),
        help_text=_("Roles in this group.")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    
    class Meta:
        verbose_name = _("Role Group")
        verbose_name_plural = _("Role Groups")
        ordering = ['name']
    
    def __str__(self) -> str:
        return str(self.name)
    
    def add_role(self, role) -> None:
        """Add a role to this group"""
        self.roles.add(role)  # type: ignore
    
    def remove_role(self, role) -> None:
        """Remove a role from this group"""
        self.roles.remove(role)  # type: ignore