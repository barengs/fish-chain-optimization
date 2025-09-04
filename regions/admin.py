from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from .models import FishingArea

@admin.register(FishingArea)
class FishingAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('template/', self.admin_site.admin_view(self.download_template_view), name='regions_fishingarea_template'),
        ]
        return custom_urls + urls
    
    def download_template_view(self, request):
        # Define the path to the template file
        template_path = os.path.join(settings.BASE_DIR, 'regions', 'templates', 'regions', 'fishing_areas_import_template.xlsx')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            return HttpResponse('Template file not found', status=404)
        
        # Serve the file
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="fishing_areas_import_template.xlsx"'
        return response