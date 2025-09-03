from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Ship
from .views import ShipImportView

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
            path('import/', self.admin_site.admin_view(self.import_ships_view), name='ships_ship_import'),
        ]
        return custom_urls + urls
    
    def import_ships_view(self, request):
        if request.method == 'POST':
            # Handle file upload
            uploaded_file = request.FILES.get('import_file')
            if uploaded_file:
                # Process the file using the existing import logic
                import_view = ShipImportView()
                import_view.request = request
                import_view.format_kwarg = {}
                
                # Create a mock request with the file
                mock_request = type('MockRequest', (), {
                    'FILES': {'file': uploaded_file},
                    'data': {}
                })()
                
                response = import_view.post(mock_request)
                
                if response.status_code == 201:
                    messages.success(request, f"Successfully imported ships: {response.data.get('imported_count', 0)}")
                else:
                    messages.error(request, f"Import failed: {response.data}")
                
                return HttpResponseRedirect("../")
            else:
                messages.error(request, "No file uploaded")
        
        # Since we don't need templates, redirect to the ships list
        messages.info(request, "Use the API endpoint for importing ships.")
        return HttpResponseRedirect("../")