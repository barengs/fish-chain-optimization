from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, OwnerProfile, CaptainProfile, OwnerType
# Import the RoleSerializer from role_managements using string reference
# from role_managements.serializers import RoleSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for JWT token pair that includes user profile in the response.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims here if needed
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user profile information to the response
        # self.user is guaranteed to be set after super().validate(attrs)
        user: CustomUser = self.user  # type: ignore
        
        # Initialize user data
        user_data = {
            'id': user.id,  # type: ignore
            'username': user.username,  # type: ignore
            'email': user.email,  # type: ignore
            'role': None,
            'profile': {}
        }
        
        # Add role information if available
        if user.role:  # type: ignore
            # Lazy import to avoid circular import
            from role_managements.serializers import RoleSerializer
            user_data['role'] = RoleSerializer(user.role).data  # type: ignore
        
        # Get the user profile based on their role
        user_profile = {}
        
        # Check if user has an owner profile
        if hasattr(user, 'owner_profile') and user.owner_profile:  # type: ignore
            owner_profile: OwnerProfile = user.owner_profile  # type: ignore
            if owner_profile.type_owner == OwnerType.INDIVIDUAL:
                user_profile['type'] = 'owner'
                user_profile['owner_type'] = 'individual'
                user_profile['first_name'] = owner_profile.first_name
                user_profile['last_name'] = owner_profile.last_name
                user_profile['id_number'] = owner_profile.id_number
                user_profile['phone_number'] = owner_profile.phone_number
                user_profile['address'] = owner_profile.address
            elif owner_profile.type_owner == OwnerType.COMPANY:
                user_profile['type'] = 'owner'
                user_profile['owner_type'] = 'company'
                user_profile['company_name'] = owner_profile.company_name
                user_profile['company_registration_number'] = owner_profile.company_registration_number
                user_profile['tax_number'] = owner_profile.tax_number
                user_profile['contact_person'] = owner_profile.contact_person
                user_profile['phone_number'] = owner_profile.phone_number
                user_profile['address'] = owner_profile.address
        
        # Check if user has a captain profile
        elif hasattr(user, 'captain_profile') and user.captain_profile:  # type: ignore
            captain_profile: CaptainProfile = user.captain_profile  # type: ignore
            user_profile['type'] = 'captain'
            user_profile['first_name'] = captain_profile.first_name
            user_profile['last_name'] = captain_profile.last_name
            user_profile['license_number'] = captain_profile.license_number
            user_profile['years_of_experience'] = captain_profile.years_of_experience
            user_profile['phone_number'] = captain_profile.phone_number
            user_profile['address'] = captain_profile.address
        
        # Add profile data
        user_data['profile'] = user_profile
        
        # Add user data to response
        data['user'] = user_data  # type: ignore
        
        return data

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