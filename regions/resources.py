from import_export import resources
from .models import FishingArea

class FishingAreaResource(resources.ModelResource):
    class Meta:
        model = FishingArea
        fields = (
            'id', 'name', 'code', 'description',
            'created_at', 'updated_at'
        )
        export_order = fields