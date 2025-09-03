from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import io
from openpyxl import Workbook
from .models import FishingArea
from .serializers import (
    FishingAreaSerializer, FishingAreaCreateUpdateSerializer, FishingAreaListSerializer
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
