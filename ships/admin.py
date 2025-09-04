from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from import_export.admin import ImportExportModelAdmin
from .models import Ship
from .resources import ShipResource

@admin.register(Ship)
class ShipAdmin(ImportExportModelAdmin):
    resource_class = ShipResource
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
        # Define the path to the template file
        template_path = os.path.join(settings.BASE_DIR, 'ships', 'templates', 'ships', 'ships_import_template.xlsx')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            return HttpResponse('Template file not found', status=404)
        
        # Serve the file
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ships_import_template.xlsx"'
        return response