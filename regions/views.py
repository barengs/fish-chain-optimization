from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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
