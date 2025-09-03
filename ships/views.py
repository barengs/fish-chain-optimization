from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import pandas as pd
import io
from .models import Ship
from .serializers import (
    ShipSerializer, ShipCreateUpdateSerializer, ShipListSerializer
)
from users.models import OwnerProfile, CaptainProfile

@extend_schema(tags=['Ships'])
class ShipListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all ships",
        description="Get a list of all ships in the system",
        responses={200: ShipListSerializer(many=True)}
    )
    def get(self, request):
        ships = Ship.objects.all()  # type: ignore
        serializer = ShipListSerializer(ships, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Ships'])
class ShipDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get ship details",
        description="Get detailed information about a specific ship",
        responses={200: ShipSerializer}
    )
    def get(self, request, pk):
        ship = get_object_or_404(Ship, pk=pk)
        serializer = ShipSerializer(ship)
        return Response(serializer.data)

@extend_schema(tags=['Ships'])
class ShipCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Create a new ship",
        description="Create a new ship with name, registration number, owner, and other details",
        request=ShipCreateUpdateSerializer,
        responses={201: ShipSerializer}
    )
    def post(self, request):
        serializer = ShipCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            ship = serializer.save()
            return Response(ShipSerializer(ship).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Ships'])
class ShipUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Update a ship",
        description="Update an existing ship's information",
        request=ShipCreateUpdateSerializer,
        responses={200: ShipSerializer}
    )
    def put(self, request, pk):
        ship = get_object_or_404(Ship, pk=pk)
        serializer = ShipCreateUpdateSerializer(ship, data=request.data)
        if serializer.is_valid():
            ship = serializer.save()
            return Response(ShipSerializer(ship).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Ships'])
class ShipDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Delete a ship",
        description="Delete a specific ship from the system",
        responses={204: None}
    )
    def delete(self, request, pk):
        ship = get_object_or_404(Ship, pk=pk)
        ship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Ships'])
class ShipTemplateDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Download ship import template",
        description="Download an Excel template file for importing ships data",
        responses={
            200: OpenApiTypes.BINARY
        }
    )
    def get(self, request):
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

@extend_schema(tags=['Ships'])
class ShipImportView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Import ships from Excel/CSV",
        description="Import ship data from an Excel or CSV file using django-import-export",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary'
                    }
                }
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'imported': {'type': 'integer'},
                    'updated': {'type': 'integer'},
                    'skipped': {'type': 'integer'},
                    'errors': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    )
    def post(self, request):
        from .resources import ShipResource
        from import_export.results import RowResult
        from tablib import Dataset
        
        # Check if file is provided
        if 'file' not in request.FILES:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the uploaded file
            file = request.FILES['file']
            
            # Validate file type
            if not (file.name.endswith('.xlsx') or file.name.endswith('.xls') or file.name.endswith('.csv')):
                return Response(
                    {"error": "Only Excel (.xlsx, .xls) or CSV (.csv) files are allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read the file content
            dataset = Dataset()
            
            # Handle different file types
            if file.name.endswith('.csv'):
                # For CSV files, we need to decode the content
                decoded_file = file.read().decode('utf-8')
                dataset.csv = decoded_file
            else:
                # For Excel files, we can load directly
                dataset.load(file.read())
            
            # Create resource instance
            resource = ShipResource()
            
            # Import data
            result = resource.import_data(
                dataset,
                dry_run=False,  # Actually import the data
                raise_errors=False
            )
            
            # Prepare response
            response_data = {
                "message": "Import completed successfully",
                "imported": result.totals[RowResult.IMPORT_TYPE_NEW],
                "updated": result.totals[RowResult.IMPORT_TYPE_UPDATE],
                "skipped": result.totals[RowResult.IMPORT_TYPE_SKIP],
                "errors": []
            }
            
            # Add errors if any
            if result.has_errors():
                errors = []
                for row_error in result.row_errors():
                    row_index, error_list = row_error
                    for error in error_list:
                        errors.append(f"Row {row_index}: {str(error)}")
                response_data["errors"] = errors
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to import ships: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )