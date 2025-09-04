from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from .models import Ship
from users.models import OwnerProfile, CaptainProfile

class ShipResource(resources.ModelResource):
    # Define fields for export
    owner_name = Field(attribute='owner', widget=ForeignKeyWidget(OwnerProfile, 'first_name'))
    captain_name = Field(attribute='captain', widget=ForeignKeyWidget(CaptainProfile, 'first_name'))
    
    class Meta:
        model = Ship
        fields = (
            'id', 'name', 'registration_number', 'owner_name', 'captain_name',
            'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active',
            'created_at', 'updated_at'
        )
        export_order = fields
        
    def dehydrate_owner_name(self, ship):
        """Return owner name based on owner type"""
        if ship.owner.type_owner == 'individual':
            return f"{ship.owner.first_name} {ship.owner.last_name}"
        else:
            return ship.owner.company_name
    
    def dehydrate_captain_name(self, ship):
        """Return captain name"""
        if ship.captain:
            return f"{ship.captain.first_name} {ship.captain.last_name}"
        return ""

    def before_import_row(self, row, **kwargs):
        """
        Process each row before importing.
        """
        # Handle empty values
        for field in ['length', 'width', 'gross_tonnage', 'year_built']:
            if field in row and row[field] == '':
                row[field] = None

        # Handle active field
        if 'active' in row and row['active'] == '':
            row['active'] = True

        # Handle captain_id
        if 'captain_id' in row and row['captain_id'] == '':
            row['captain_id'] = None

        return row

    def save_instance(self, instance, is_create, using_transactions=True, dry_run=False):
        """
        Save the instance.
        """
        if not dry_run:
            instance.save()
        return instance