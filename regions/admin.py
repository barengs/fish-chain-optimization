from django.contrib import admin
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
            path('import/', self.admin_site.admin_view(self.import_fishing_areas_view), name='regions_fishingarea_import'),
        ]
        return custom_urls + urls
    
    def import_fishing_areas_view(self, request):
        if request.method == 'POST':
            # Handle file upload
            uploaded_file = request.FILES.get('import_file')
            if uploaded_file:
                # Process the file using the existing import logic
                import_view = FishingAreaImportView()
                import_view.request = request
                import_view.format_kwarg = {}
                
                # Create a mock request with the file
                mock_request = type('MockRequest', (), {
                    'FILES': {'file': uploaded_file},
                    'data': {}
                })()
                
                response = import_view.post(mock_request)
                
                if response.status_code == 201:
                    messages.success(request, f"Successfully imported fishing areas: {response.data.get('imported_count', 0)}")
                else:
                    messages.error(request, f"Import failed: {response.data}")
                
                return HttpResponseRedirect("../")
            else:
                messages.error(request, "No file uploaded")
        
        # Since we don't need templates, redirect to the fishing areas list
        messages.info(request, "Use the API endpoint for importing fishing areas.")
        return HttpResponseRedirect("../")
