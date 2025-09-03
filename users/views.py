from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .serializers import CustomUserSerializer, CustomUserCreateSerializer, IndividualOwnerProfileSerializer, CompanyOwnerProfileSerializer, CaptainProfileSerializer, OwnerProfileSerializer, CustomTokenObtainPairSerializer
from .models import CustomUser, OwnerProfile, OwnerType
# Import role management models
from role_managements.models import Role as ManagementRole

@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT token pairs that includes user profile in the response.
    """
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(tags=['Authentication'])
class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Register a new user with username, email, password and optional role",
        request=CustomUserCreateSerializer,
        responses={201: CustomUserSerializer}
    )
    def post(self, request):
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  # type: ignore
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authentication'])
class RegisterOwnerView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new owner user",
        description="Register a new owner user (individual or company) with profile information",
        request=CustomUserCreateSerializer,
        responses={201: CustomUserSerializer}
    )
    def post(self, request):
        # Get the dynamic role for owner
        try:
            owner_role = ManagementRole.objects.get(name='Pemilik Kapal')  # type: ignore
        except ManagementRole.DoesNotExist:  # type: ignore
            # Fallback to first available role or create a default one
            owner_role = None
        
        # Extract user data and profile data
        user_data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'password2': request.data.get('password2')
        }
        
        # Add role if found
        if owner_role:
            user_data['role_id'] = owner_role.id
        
        user_serializer = CustomUserCreateSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            
            # Create owner profile based on owner type
            owner_type = request.data.get('owner_type', 'individual')
            profile_data = request.data.get('profile', {})
            profile_data['user'] = user  # type: ignore
            
            if owner_type == 'individual':
                profile_data['type_owner'] = OwnerType.INDIVIDUAL
                profile_serializer = IndividualOwnerProfileSerializer(data=profile_data)
            elif owner_type == 'company':
                profile_data['type_owner'] = OwnerType.COMPANY
                profile_serializer = CompanyOwnerProfileSerializer(data=profile_data)
            else:
                user.delete()  # type: ignore # Delete user if no valid owner type
                return Response({'error': 'Invalid owner type'}, status=status.HTTP_400_BAD_REQUEST)
            
            if profile_serializer.is_valid():
                # Use the general OwnerProfileSerializer to save
                owner_profile_serializer = OwnerProfileSerializer(data=profile_serializer.validated_data)
                if owner_profile_serializer.is_valid():
                    owner_profile_serializer.save()
                
                refresh = RefreshToken.for_user(user)  # type: ignore
                return Response({
                    'user': CustomUserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            else:
                user.delete()  # type: ignore # Delete user if profile creation fails
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authentication'])
class RegisterCaptainView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new captain user",
        description="Register a new captain user with profile information",
        request=CustomUserCreateSerializer,
        responses={201: CustomUserSerializer}
    )
    def post(self, request):
        # Get the dynamic role for captain
        try:
            captain_role = ManagementRole.objects.get(name='Nahkoda Kapal')  # type: ignore
        except ManagementRole.DoesNotExist:  # type: ignore
            # Fallback to first available role or create a default one
            captain_role = None
        
        # Extract user data and profile data
        user_data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'password2': request.data.get('password2')
        }
        
        # Add role if found
        if captain_role:
            user_data['role_id'] = captain_role.id
        
        user_serializer = CustomUserCreateSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            
            # Create captain profile
            profile_data = request.data.get('profile', {})
            profile_data['user'] = user  # type: ignore
            profile_serializer = CaptainProfileSerializer(data=profile_data)
            
            if profile_serializer.is_valid():
                profile_serializer.save()
                refresh = RefreshToken.for_user(user)  # type: ignore
                return Response({
                    'user': CustomUserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            else:
                user.delete()  # type: ignore # Delete user if profile creation fails
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    @extend_schema(
        summary="Logout user",
        description="Logout the current user by blacklisting the refresh token",
        request={
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string'}
            }
        },
        responses={205: None}
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)