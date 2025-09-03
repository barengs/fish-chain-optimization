from django.contrib import admin
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
        from django.urls import path
        from . import views
        urls = super().get_urls()
        custom_urls = [
            path('import-ships/', self.admin_site.admin_view(self.import_ships_view), name='ships_import'),
        ]
        return custom_urls + urls
    
    def import_ships_view(self, request):
        from django.shortcuts import render, redirect
        from django.contrib import messages
        from .serializers import ShipImportSerializer
        
        if request.method == 'POST':
            serializer = ShipImportSerializer(data=request.POST, files=request.FILES)
            if serializer.is_valid():
                try:
                    # Create a mock request object for the view
                    from django.core.files.uploadedfile import UploadedFile
                    from rest_framework.request import Request
                    from rest_framework.parsers import MultiPartParser
                    from django.http import HttpRequest
                    
                    # Create a mock DRF request
                    http_request = HttpRequest()
                    http_request.META = request.META
                    http_request.method = 'POST'
                    http_request.POST = request.POST
                    http_request.FILES = request.FILES
                    
                    # Create DRF request
                    drf_request = Request(http_request)
                    drf_request._full_data = request.POST
                    drf_request.FILES = request.FILES
                    
                    # Call the import view method
                    view = views.ShipImportView()
                    view.request = drf_request
                    response = view.post(drf_request)
                    
                    if response.status_code == 201:
                        messages.success(request, response.data['message'])
                    else:
                        messages.error(request, response.data.get('error', 'Failed to import ships'))
                except Exception as e:
                    messages.error(request, f"Error importing ships: {str(e)}")
            else:
                messages.error(request, f"Invalid data: {serializer.errors}")
            return redirect('admin:ships_ship_changelist')
        
        context = {
            'title': 'Import Ships',
            'has_permission': True,
            'site_url': '/admin/',
        }
        return render(request, 'admin/ships/import_ships.html', context)