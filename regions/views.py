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
from .models import FishingArea
from .serializers import (
    FishingAreaSerializer, FishingAreaCreateUpdateSerializer, FishingAreaListSerializer
)
from .resources import FishingAreaResource

@extend_schema(tags=['Fishing Areas'])
class FishingAreaListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all fishing areas",
        description="Get a list of all fishing areas in the system",
        responses={200: FishingAreaListSerializer(many=True)}
    )
    def get(self, request):
        fishing_areas = FishingArea.objects.all()  # type: ignore
        serializer = FishingAreaListSerializer(fishing_areas, many=True)
        return Response(serializer.data)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get fishing area details",
        description="Get detailed information about a specific fishing area",
        responses={200: FishingAreaSerializer}
    )
    def get(self, request, pk):
        fishing_area = get_object_or_404(FishingArea, pk=pk)
        serializer = FishingAreaSerializer(fishing_area)
        return Response(serializer.data)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Create a new fishing area",
        description="Create a new fishing area with name, code, and other details",
        request=FishingAreaCreateUpdateSerializer,
        responses={201: FishingAreaSerializer}
    )
    def post(self, request):
        serializer = FishingAreaCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            fishing_area = serializer.save()
            return Response(FishingAreaSerializer(fishing_area).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Update a fishing area",
        description="Update an existing fishing area's information",
        request=FishingAreaCreateUpdateSerializer,
        responses={200: FishingAreaSerializer}
    )
    def put(self, request, pk):
        fishing_area = get_object_or_404(FishingArea, pk=pk)
        serializer = FishingAreaCreateUpdateSerializer(fishing_area, data=request.data)
        if serializer.is_valid():
            fishing_area = serializer.save()
            return Response(FishingAreaSerializer(fishing_area).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Delete a fishing area",
        description="Delete a specific fishing area from the system",
        responses={204: None}
    )
    def delete(self, request, pk):
        fishing_area = get_object_or_404(FishingArea, pk=pk)
        fishing_area.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaTemplateDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Download fishing area import template",
        description="Download an Excel template file for importing fishing areas data",
        responses={
            200: OpenApiTypes.BINARY
        }
    )
    def get(self, request):
        # Define the path to the template file
        template_path = os.path.join(settings.BASE_DIR, 'regions', 'templates', 'regions', 'fishing_areas_import_template.xlsx')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            return Response({'error': 'Template file not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serve the file
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="fishing_areas_import_template.xlsx"'
        return response

@extend_schema(tags=['Fishing Areas'])
class FishingAreaImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @extend_schema(
        summary="Import fishing areas from Excel/CSV",
        description="Import multiple fishing areas from an Excel or CSV file",
        request={
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Excel or CSV file containing fishing area data'
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
            resource = FishingAreaResource()
            dataset = format_class().create_dataset(file.read())
            result = resource.import_data(dataset, dry_run=False)
            
            return Response({
                'message': f'Successfully imported {result.total_rows} fishing areas',
                'imported_count': result.total_rows
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'Failed to import fishing areas: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Fishing Areas'])
class FishingAreaExportView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Export fishing areas to Excel/CSV",
        description="Export all fishing areas data to Excel or CSV format",
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
            resource = FishingAreaResource()
            dataset = resource.export()
            
            if format_type == 'csv':
                export_data = dataset.csv
                content_type = 'text/csv'
                filename = 'fishing_areas_export.csv'
            else:
                export_data = dataset.xlsx
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = 'fishing_areas_export.xlsx'
            
            response = HttpResponse(export_data, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            return Response({'error': f'Failed to export fishing areas: {str(e)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
