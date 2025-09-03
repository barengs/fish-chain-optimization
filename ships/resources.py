from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from .models import Ship
from users.models import OwnerProfile, CaptainProfile


class ShipResource(resources.ModelResource):
    owner = Field(
        column_name='owner_id',
        attribute='owner',
        widget=ForeignKeyWidget(OwnerProfile, 'id')
    )
    captain = Field(
        column_name='captain_id',
        attribute='captain',
        widget=ForeignKeyWidget(CaptainProfile, 'id')
    )

    class Meta:
        model = Ship
        fields = (
            'id', 'name', 'registration_number', 'owner', 'captain',
            'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active'
        )
        export_order = fields
        import_id_fields = ('registration_number',)
        skip_unchanged = True
        report_skipped = True

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