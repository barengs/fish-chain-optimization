from django.contrib import admin
from django.urls import path
from .models import Ship

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'get_owner_name', 'get_captain_name', 'active')
    list_filter = ('active', 'year_built', 'home_port')
    search_fields = ('name', 'registration_number', 'owner__first_name', 'owner__last_name', 'owner__company_name')
    readonly_fields = ('created_at', 'updated_at')
    
    @admin.display(description='Owner')
    def get_owner_name(self, obj):
        if obj.owner.type_owner == 'individual':
            return f"{obj.owner.first_name} {obj.owner.last_name}"
        else:
            return obj.owner.company_name
    
    @admin.display(description='Captain')
    def get_captain_name(self, obj):
        if obj.captain:
            return f"{obj.captain.first_name} {obj.captain.last_name}"
        return "No Captain"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('template/', self.admin_site.admin_view(self.download_template_view), name='ships_ship_template'),
        ]
        return custom_urls + urls
    
    def download_template_view(self, request):
        from django.http import HttpResponse
        import pandas as pd
        import io
        
        # Create a DataFrame with template data
        template_data = {
            'name': ['Example Ship Name'],
            'registration_number': ['EX123456'],
            'owner_name': ['John Doe'],  # Can be individual or company name
            'captain_name': ['Captain Smith'],  # Optional
            'length': [20.5],  # in meters
            'width': [5.2],  # in meters
            'gross_tonnage': [100.5],
            'year_built': [2020],
            'home_port': ['Port City'],
            'active': [True]
        }
        
        df = pd.DataFrame(template_data)
        
        # Create an Excel file in memory
        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Ships_Template')
        writer.close()
        
        # Prepare the response
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ships_import_template.xlsx"'
        return response