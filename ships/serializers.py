from rest_framework import serializers
from .models import Ship
from users.serializers import OwnerProfileSerializer, CaptainProfileSerializer

class ShipSerializer(serializers.ModelSerializer):
    """
    Serializer for ship details.
    
    This serializer includes ship information along with owner and captain details.
    """
    owner = OwnerProfileSerializer(read_only=True)
    captain = CaptainProfileSerializer(read_only=True, allow_null=True)
    
    class Meta:
        model = Ship
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ShipCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating ships.
    
    This serializer is used when creating new ships or updating existing ones.
    It allows specifying owner and captain IDs.
    """
    owner_id = serializers.IntegerField(write_only=True)
    captain_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Ship
        fields = (
            'id', 'name', 'registration_number', 'owner_id', 'captain_id',
            'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active'
        )
    
    def create(self, validated_data):
        owner_id = validated_data.pop('owner_id')
        captain_id = validated_data.pop('captain_id', None)
        
        # Get the owner and captain profiles
        from users.models import OwnerProfile, CaptainProfile
        owner = OwnerProfile.objects.get(id=owner_id)  # type: ignore
        captain = CaptainProfile.objects.get(id=captain_id) if captain_id else None  # type: ignore
        
        # Create the ship
        ship = Ship.objects.create(  # type: ignore
            owner=owner,
            captain=captain,
            **validated_data
        )
        return ship
    
    def update(self, instance, validated_data):
        owner_id = validated_data.pop('owner_id', None)
        captain_id = validated_data.pop('captain_id', None)
        
        # Update owner if provided
        if owner_id:
            from users.models import OwnerProfile
            owner = OwnerProfile.objects.get(id=owner_id)  # type: ignore
            instance.owner = owner
        
        # Update captain if provided
        if captain_id is not None:
            from users.models import CaptainProfile
            captain = CaptainProfile.objects.get(id=captain_id) if captain_id else None  # type: ignore
            instance.captain = captain
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class ShipListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing ships with minimal information.
    
    This serializer is used for listing ships with only essential information.
    """
    owner_name = serializers.SerializerMethodField()
    captain_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Ship
        fields = (
            'id', 'name', 'registration_number', 'owner_name', 'captain_name',
            'length', 'width', 'gross_tonnage', 'active'
        )
    
    def get_owner_name(self, obj):
        """Get the owner name based on owner type"""
        if obj.owner.type_owner == 'individual':
            return f"{obj.owner.first_name} {obj.owner.last_name}"
        else:
            return obj.owner.company_name
    
    def get_captain_name(self, obj):
        """Get the captain name"""
        if obj.captain:
            return f"{obj.captain.first_name} {obj.captain.last_name}"
        return None

class ShipImportSerializer(serializers.Serializer):
    """
    Serializer for importing ships from Excel/CSV files.
    """
    file = serializers.FileField(required=True, help_text="Excel or CSV file containing ship data")
    
    def validate_file(self, value):
        """
        Validate that the uploaded file is either Excel or CSV.
        """
        if not value:
            raise serializers.ValidationError("No file uploaded")
            
        # Check file extension
        file_name = value.name.lower()
        if not (file_name.endswith('.xlsx') or file_name.endswith('.xls') or file_name.endswith('.csv')):
            raise serializers.ValidationError("Only Excel (.xlsx, .xls) or CSV (.csv) files are allowed")
            
        return value