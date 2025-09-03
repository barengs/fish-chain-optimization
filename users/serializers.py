from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, OwnerProfile, CaptainProfile, OwnerType
# Import the RoleSerializer from role_managements using string reference
# from role_managements.serializers import RoleSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.
    
    This serializer is used to serialize user information including their role.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    # Use the RoleSerializer for the role field (will be defined later)
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_role(self, obj):
        # Lazy import to avoid circular import
        from role_managements.serializers import RoleSerializer
        if obj.role:
            return RoleSerializer(obj.role).data
        return None
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords must match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    
    This serializer is used when registering new users and allows specifying
    a role ID for the user.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    # For creation, we might want to accept role ID
    role_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role_id', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords must match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        role_id = validated_data.pop('role_id', None)
        password = validated_data.pop('password')
        
        user = CustomUser(**validated_data)
        user.set_password(password)
        
        # Set the role if provided
        if role_id:
            from role_managements.models import Role as ManagementRole
            try:
                role = ManagementRole.objects.get(id=role_id)  # type: ignore
                user.role = role
            except ManagementRole.DoesNotExist:  # type: ignore
                pass
        
        user.save()
        return user

class IndividualOwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for individual owner profiles.
    
    This serializer is used specifically for individual owners and includes
    fields relevant to individual users.
    """
    class Meta:
        model = OwnerProfile
        fields = ('first_name', 'last_name', 'id_number', 'phone_number', 'address')
    
    def validate(self, attrs):
        # Validate individual owner required fields
        if not attrs.get('first_name'):
            raise serializers.ValidationError("First name is required for individual owners")
        if not attrs.get('last_name'):
            raise serializers.ValidationError("Last name is required for individual owners")
        if not attrs.get('id_number'):
            raise serializers.ValidationError("ID number is required for individual owners")
        return attrs

class CompanyOwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for company owner profiles.
    
    This serializer is used specifically for company owners and includes
    fields relevant to company users.
    """
    class Meta:
        model = OwnerProfile
        fields = ('company_name', 'company_registration_number', 'tax_number', 'contact_person', 'phone_number', 'address')
    
    def validate(self, attrs):
        # Validate company owner required fields
        if not attrs.get('company_name'):
            raise serializers.ValidationError("Company name is required for company owners")
        if not attrs.get('company_registration_number'):
            raise serializers.ValidationError("Company registration number is required for company owners")
        if not attrs.get('tax_number'):
            raise serializers.ValidationError("Tax number is required for company owners")
        if not attrs.get('contact_person'):
            raise serializers.ValidationError("Contact person is required for company owners")
        return attrs

class OwnerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for owner profiles.
    
    This serializer handles both individual and company owner profiles
    and includes validation for both types.
    """
    class Meta:
        model = OwnerProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        type_owner = attrs.get('type_owner')
        
        if type_owner == OwnerType.INDIVIDUAL:
            # Validate individual owner required fields
            if not attrs.get('first_name'):
                raise serializers.ValidationError("First name is required for individual owners")
            if not attrs.get('last_name'):
                raise serializers.ValidationError("Last name is required for individual owners")
            if not attrs.get('id_number'):
                raise serializers.ValidationError("ID number is required for individual owners")
                
        elif type_owner == OwnerType.COMPANY:
            # Validate company owner required fields
            if not attrs.get('company_name'):
                raise serializers.ValidationError("Company name is required for company owners")
            if not attrs.get('company_registration_number'):
                raise serializers.ValidationError("Company registration number is required for company owners")
            if not attrs.get('tax_number'):
                raise serializers.ValidationError("Tax number is required for company owners")
            if not attrs.get('contact_person'):
                raise serializers.ValidationError("Contact person is required for company owners")
                
        return attrs

class CaptainProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for captain profiles.
    
    This serializer is used for captain users and includes
    fields relevant to ship captains.
    """
    class Meta:
        model = CaptainProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for complete user profile.
    
    This serializer includes user information along with their role and profiles.
    """
    role = serializers.SerializerMethodField()
    owner_profile = OwnerProfileSerializer(read_only=True)
    captain_profile = CaptainProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'role', 'owner_profile', 'captain_profile')
    
    def get_role(self, obj):
        # Lazy import to avoid circular import
        from role_managements.serializers import RoleSerializer
        if obj.role:
            return RoleSerializer(obj.role).data
        return None