from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Custom User model that extends Django's built-in User model.
    
    This model adds a role field that references the dynamic Role model
    from the role management system.
    """
    # Remove the static Role enum and use a ForeignKey to the dynamic Role model
    # Use string reference to avoid circular import
    role = models.ForeignKey(
        'role_managements.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Role")
    )
    
    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        return f"{self.username} ({role_name})"

class OwnerType(models.TextChoices):
    """
    Choices for owner types.
    
    Defines the different types of owners in the system:
    - Individual: A single person owner
    - Company: A corporate entity owner
    """
    INDIVIDUAL = 'individual', _('Individual')
    COMPANY = 'company', _('Company')

class OwnerProfile(models.Model):
    """
    Owner profile model that handles both individual and company owners.
    
    This model uses a type_owner field to differentiate between individual
    and company owners, with appropriate fields for each type.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='owner_profile')
    type_owner = models.CharField(
        max_length=20,
        choices=OwnerType.choices,
        verbose_name=_("Owner Type")
    )
    
    # Individual owner fields
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)  # NIK or similar ID
    
    # Company owner fields
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_registration_number = models.CharField(max_length=30, blank=True, null=True)
    tax_number = models.CharField(max_length=30, blank=True, null=True)  # NPWP or similar
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    
    # Common fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.type_owner == OwnerType.INDIVIDUAL and self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.type_owner == OwnerType.COMPANY and self.company_name:
            return str(self.company_name)
        else:
            return f"Owner Profile ({self.type_owner})"

class CaptainProfile(models.Model):
    """
    Captain profile model.
    
    This model stores information specific to ship captains.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='captain_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    license_number = models.CharField(max_length=30, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)  # type: ignore
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (License: {self.license_number})"