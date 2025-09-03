from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
import io
from openpyxl import Workbook
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
        # Create a workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Ships_Template"
        
        # Add headers
        headers = [
            'name', 'registration_number', 'owner_name', 'captain_name',
            'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active'
        ]
        ws.append(headers)
        
        # Add sample data
        sample_data = [
            'Example Ship Name', 'EX123456', 'John Doe', 'Captain Smith',
            20.5, 5.2, 100.5, 2020, 'Port City', True
        ]
        ws.append(sample_data)
        
        # Create an in-memory buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # Prepare the response
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ships_import_template.xlsx"'
        return response