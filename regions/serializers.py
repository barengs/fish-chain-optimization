from rest_framework import serializers
from .models import FishingArea

class FishingAreaSerializer(serializers.ModelSerializer):
    """
    Serializer for fishing area details.
    
    This serializer includes all fishing area information.
    """
    
    class Meta:
        model = FishingArea
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class FishingAreaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating fishing areas.
    
    This serializer is used when creating new fishing areas or updating existing ones.
    """
    
    class Meta:
        model = FishingArea
        fields = (
            'id', 'name', 'code', 'description'
        )

class FishingAreaListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing fishing areas with minimal information.
    
    This serializer is used for listing fishing areas with only essential information.
    """
    
    class Meta:
        model = FishingArea
        fields = (
            'id', 'name', 'code'
        )

class FishingAreaImportSerializer(serializers.Serializer):
    """
    Serializer for importing fishing areas from Excel/CSV files.
    
    This serializer validates the import file data.
    """
    file = serializers.FileField(required=True, help_text="Excel or CSV file containing fishing area data")
    
    def validate_file(self, value):
        """Validate that the uploaded file is either Excel or CSV"""
        if not value:
            raise serializers.ValidationError("No file uploaded")
        
        # Check file extension
        filename = value.name.lower()
        if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
            raise serializers.ValidationError("File must be Excel (.xlsx, .xls) or CSV (.csv) format")
        
        return value

class FishingAreaImportDataSerializer(serializers.ModelSerializer):
    """
    Serializer for validating individual fishing area data during import.
    
    This serializer is used to validate each row of data during import.
    """
    
    class Meta:
        model = FishingArea
        fields = (
            'name', 'code', 'description'
        )