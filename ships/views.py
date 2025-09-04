from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from import_export.formats.base_formats import XLSX, CSV
from .models import Ship
from .serializers import (
    ShipSerializer, ShipCreateUpdateSerializer, ShipListSerializer
)
from .resources import ShipResource
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
        # Define the path to the template file
        template_path = os.path.join(settings.BASE_DIR, 'ships', 'templates', 'ships', 'ships_import_template.xlsx')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            return Response({'error': 'Template file not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serve the file
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="ships_import_template.xlsx"'
        return response

@extend_schema(tags=['Ships'])
class ShipImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @extend_schema(
        summary="Import ships from Excel/CSV",
        description="Import multiple ships from an Excel or CSV file",
        request={
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Excel or CSV file containing ship data'
                }
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'imported_count': {'type': 'integer'}
                }
            }
        }
    )
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine file format
        if file.name.endswith('.xlsx'):
            format_class = XLSX
        elif file.name.endswith('.csv'):
            format_class = CSV
        else:
            return Response({'error': 'Unsupported file format. Please upload Excel (.xlsx) or CSV (.csv) files.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Import data using django-import-export
        try:
            resource = ShipResource()
            dataset = format_class().create_dataset(file.read())
            result = resource.import_data(dataset, dry_run=False)
            
            return Response({
                'message': f'Successfully imported {result.total_rows} ships',
                'imported_count': result.total_rows
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'Failed to import ships: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Ships'])
class ShipExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Export ships to Excel/CSV",
        description="Export all ships data to Excel or CSV format",
        parameters=[
            OpenApiParameter(
                name='format',
                description='Export format',
                required=False,
                type=str,
                enum=['xlsx', 'csv'],
                default='xlsx'
            )
        ],
        responses={
            200: OpenApiTypes.BINARY
        }
    )
    def get(self, request):
        format_type = request.query_params.get('format', 'xlsx')
        
        # Export data using django-import-export
        try:
            resource = ShipResource()
            dataset = resource.export()
            
            if format_type == 'csv':
                export_data = dataset.csv
                content_type = 'text/csv'
                filename = 'ships_export.csv'
            else:
                export_data = dataset.xlsx
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = 'ships_export.xlsx'
            
            response = HttpResponse(export_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return Response({'error': f'Failed to export ships: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
