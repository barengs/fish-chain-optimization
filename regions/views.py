from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import pandas as pd
import io
from .models import FishingArea
from .serializers import (
    FishingAreaSerializer, FishingAreaCreateUpdateSerializer, FishingAreaListSerializer,
    FishingAreaImportSerializer, FishingAreaImportDataSerializer
)

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

@extend_schema(tags=['Fishing Areas'])
class FishingAreaImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    @extend_schema(
        summary="Import fishing areas from Excel/CSV",
        description="Import multiple fishing areas from an Excel or CSV file",
        request=FishingAreaImportSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'imported_count': {'type': 'integer'},
                    'errors': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    )
    def post(self, request):
        serializer = FishingAreaImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read the file based on its extension
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:  # Excel file
                df = pd.read_excel(file)
            
            # Process the data
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Prepare data for validation
                    fishing_area_data = {
                        'name': row.get('name'),
                        'code': row.get('code'),
                        'description': row.get('description', '')
                    }
                    
                    # Validate the data
                    import_serializer = FishingAreaImportDataSerializer(data=fishing_area_data)
                    if not import_serializer.is_valid():
                        error_msg = str(import_serializer.errors)
                        row_num = str(int(index) + 1)
                        errors.append("Row " + row_num + ": " + error_msg)
                        continue
                    
                    # Create or update fishing area
                    fishing_area, created = FishingArea.objects.get_or_create(  # type: ignore
                        code=fishing_area_data['code'],
                        defaults={
                            'name': fishing_area_data['name'],
                            'description': fishing_area_data['description']
                        }
                    )
                    
                    if not created:
                        # Update existing fishing area
                        fishing_area.name = fishing_area_data['name']
                        fishing_area.description = fishing_area_data['description']
                        fishing_area.save()
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    row_num = str(int(index) + 1)
                    errors.append("Row " + row_num + ": " + error_msg)
                    continue
            
            return Response({
                'message': f'Successfully imported {imported_count} fishing areas',
                'imported_count': imported_count,
                'errors': errors
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_msg = str(e)
            return Response({'error': 'Failed to process file: ' + error_msg}, status=status.HTTP_400_BAD_REQUEST)