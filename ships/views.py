from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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
class ShipImportView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Import ships from Excel/CSV",
        description="Import ship data from an Excel or CSV file",
        request=ShipImportSerializer,
        responses={201: {"type": "object", "properties": {"message": {"type": "string"}, "imported_count": {"type": "integer"}}}}
    )
    def post(self, request):
        serializer = ShipImportSerializer(data=request.data)
        if serializer.is_valid():
            file = request.FILES.get('file')
            if not file:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                imported_count = self.import_ships_from_file(file)
                return Response({
                    "message": f"Successfully imported {imported_count} ships",
                    "imported_count": imported_count
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Failed to import ships: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def import_ships_from_file(self, file):
        """
        Import ships from Excel or CSV file.
        Expected columns: name, registration_number, owner_id, captain_id (optional),
        length (optional), width (optional), gross_tonnage (optional), year_built (optional),
        home_port (optional), active (optional)
        """
        import pandas as pd
        from users.models import OwnerProfile, CaptainProfile
        
        # Determine file type and read data
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:  # Excel file
            df = pd.read_excel(file)
        
        imported_count = 0
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Extract data from row
                name = row.get('name')
                registration_number = row.get('registration_number')
                owner_id = row.get('owner_id')
                captain_id = row.get('captain_id')
                
                # Skip if required fields are missing
                if not name or not registration_number or not owner_id:
                    continue
                
                # Validate owner exists
                try:
                    owner = OwnerProfile.objects.get(id=owner_id)
                except OwnerProfile.DoesNotExist:
                    continue
                
                # Validate captain if provided
                captain = None
                if captain_id:
                    try:
                        captain = CaptainProfile.objects.get(id=captain_id)
                    except CaptainProfile.DoesNotExist:
                        pass  # Captain not found, leave as None
                
                # Prepare ship data
                ship_data = {
                    'name': name,
                    'registration_number': registration_number,
                    'owner': owner,
                    'captain': captain,
                    'length': row.get('length') if pd.notna(row.get('length')) else None,
                    'width': row.get('width') if pd.notna(row.get('width')) else None,
                    'gross_tonnage': row.get('gross_tonnage') if pd.notna(row.get('gross_tonnage')) else None,
                    'year_built': row.get('year_built') if pd.notna(row.get('year_built')) else None,
                    'home_port': row.get('home_port') if pd.notna(row.get('home_port')) else None,
                    'active': row.get('active', True) if pd.notna(row.get('active')) else True,
                }
                
                # Create or update ship
                ship, created = Ship.objects.get_or_create(
                    registration_number=registration_number,
                    defaults=ship_data
                )
                
                # If ship already exists, update it
                if not created:
                    for key, value in ship_data.items():
                        setattr(ship, key, value)
                    ship.save()
                
                imported_count += 1
            except Exception as e:
                # Log error and continue with next row
                print(f"Error importing row: {e}")
                continue
        
        return imported_count