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
    parser_classes = (MultiPartParser, FormParser)
    
    @extend_schema(
        summary="Import ships from Excel/CSV",
        description="Import multiple ships from an Excel or CSV file",
        request=ShipImportSerializer,
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
        serializer = ShipImportSerializer(data=request.data)
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
                    ship_data = {
                        'name': row.get('name'),
                        'registration_number': row.get('registration_number'),
                        'owner_name': row.get('owner_name'),
                        'captain_name': row.get('captain_name', ''),
                        'length': row.get('length'),
                        'width': row.get('width'),
                        'gross_tonnage': row.get('gross_tonnage'),
                        'year_built': row.get('year_built'),
                        'home_port': row.get('home_port'),
                        'active': row.get('active', True)
                    }
                    
                    # Validate the data
                    import_serializer = ShipImportDataSerializer(data=ship_data)
                    if not import_serializer.is_valid():
                        error_msg = str(import_serializer.errors)
                        row_num = str(int(index) + 1)
                        errors.append("Row " + row_num + ": " + error_msg)
                        continue
                    
                    # Find or create owner
                    owner = None
                    try:
                        # Try to find individual owner first
                        owner_name = ship_data['owner_name']
                        if owner_name and ' ' in str(owner_name):
                            name_parts = str(owner_name).split()
                            owner = OwnerProfile.objects.get(  # type: ignore
                                first_name__icontains=name_parts[0],
                                last_name__icontains=name_parts[-1]
                            )
                        else:
                            # Try as company name
                            owner = OwnerProfile.objects.get(  # type: ignore
                                company_name__icontains=str(owner_name)
                            )
                    except OwnerProfile.DoesNotExist:  # type: ignore
                        owner_name_str = str(ship_data['owner_name'])
                        row_num = str(int(index) + 1)
                        errors.append("Row " + row_num + ": Owner '" + owner_name_str + "' not found")
                        continue
                    
                    # Find or create captain (if provided)
                    captain = None
                    captain_name = ship_data['captain_name']
                    if captain_name and ' ' in str(captain_name):
                        try:
                            captain_name_parts = str(captain_name).split()
                            captain = CaptainProfile.objects.get(  # type: ignore
                                first_name__icontains=captain_name_parts[0],
                                last_name__icontains=captain_name_parts[-1]
                            )
                        except CaptainProfile.DoesNotExist:  # type: ignore
                            captain_name_str = str(ship_data['captain_name'])
                            row_num = str(int(index) + 1)
                            errors.append("Row " + row_num + ": Captain '" + captain_name_str + "' not found")
                            continue
                    
                    # Create or update ship
                    ship, created = Ship.objects.get_or_create(  # type: ignore
                        registration_number=ship_data['registration_number'],
                        defaults={
                            'name': ship_data['name'],
                            'owner': owner,
                            'captain': captain,
                            'length': ship_data['length'],
                            'width': ship_data['width'],
                            'gross_tonnage': ship_data['gross_tonnage'],
                            'year_built': ship_data['year_built'],
                            'home_port': ship_data['home_port'],
                            'active': ship_data['active']
                        }
                    )
                    
                    if not created:
                        # Update existing ship
                        ship.name = ship_data['name']
                        ship.owner = owner
                        ship.captain = captain
                        ship.length = ship_data['length']
                        ship.width = ship_data['width']
                        ship.gross_tonnage = ship_data['gross_tonnage']
                        ship.year_built = ship_data['year_built']
                        ship.home_port = ship_data['home_port']
                        ship.active = ship_data['active']
                        ship.save()
                    
                    imported_count += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    row_num = str(int(index) + 1)
                    errors.append("Row " + row_num + ": " + error_msg)
                    continue
            
            return Response({
                'message': f'Successfully imported {imported_count} ships',
                'imported_count': imported_count,
                'errors': errors
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error_msg = str(e)
            return Response({'error': 'Failed to process file: ' + error_msg}, status=status.HTTP_400_BAD_REQUEST)