from django.contrib import admin
from django.urls import path
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
        from django.http import HttpResponse
        import pandas as pd
        import io
        
        # Create a DataFrame with template data
        template_data = {
            'name': ['Example Fishing Area'],
            'code': ['EX001'],
            'description': ['Example description for fishing area']
        }
        
        df = pd.DataFrame(template_data)
        
        # Create an Excel file in memory
        buffer = io.BytesIO()
        writer = pd.ExcelWriter(buffer, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Fishing_Areas_Template')
        writer.close()
        
        # Prepare the response
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="fishing_areas_import_template.xlsx"'
        return response