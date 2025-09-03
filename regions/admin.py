from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
import io
from openpyxl import Workbook
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
        # Create a workbook and select the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Fishing_Areas_Template"
        
        # Add headers
        headers = ['name', 'code', 'description']
        ws.append(headers)
        
        # Add sample data
        sample_data = ['Example Fishing Area', 'EX001', 'Example description for fishing area']
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
        response['Content-Disposition'] = 'attachment; filename="fishing_areas_import_template.xlsx"'
        return response