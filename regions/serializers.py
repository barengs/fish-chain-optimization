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