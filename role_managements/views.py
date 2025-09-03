from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Role, UserRole, RoleGroup
from .serializers import (
    RoleSerializer, RoleCreateUpdateSerializer, 
    UserRoleSerializer, UserRoleCreateSerializer,
    RoleGroupSerializer, RoleGroupCreateUpdateSerializer,
    PermissionSerializer
)
from users.models import CustomUser

@extend_schema(tags=['Roles'])
class RoleListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all roles",
        description="Get a list of all available roles in the system",
        responses={200: RoleSerializer(many=True)}
    )
    def get(self, request):
        roles = Role.objects.all()  # type: ignore
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create a new role",
        description="Create a new role with name, description and permissions",
        request=RoleCreateUpdateSerializer,
        responses={201: RoleSerializer}
    )
    def post(self, request):
        serializer = RoleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Roles'])
class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get role details",
        description="Get detailed information about a specific role",
        responses={200: RoleSerializer}
    )
    def get(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update a role",
        description="Update an existing role's information",
        request=RoleCreateUpdateSerializer,
        responses={200: RoleSerializer}
    )
    def put(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        serializer = RoleCreateUpdateSerializer(role, data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            return Response(RoleSerializer(role).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Delete a role",
        description="Delete a specific role from the system",
        responses={204: None}
    )
    def delete(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Permissions'])
class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all permissions",
        description="Get a list of all available permissions in the system",
        responses={200: PermissionSerializer(many=True)}
    )
    def get(self, request):
        permissions = Permission.objects.all()  # type: ignore
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

@extend_schema(tags=['User Roles'])
class UserRoleListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all user roles",
        description="Get a list of all user-role assignments in the system",
        responses={200: UserRoleSerializer(many=True)}
    )
    def get(self, request):
        user_roles = UserRole.objects.all()  # type: ignore
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Assign a role to a user",
        description="Create a new user-role assignment",
        request=UserRoleCreateSerializer,
        responses={201: UserRoleSerializer}
    )
    def post(self, request):
        # Automatically set the assigned_by to the current user
        request.data['assigned_by'] = request.user.id
        serializer = UserRoleCreateSerializer(data=request.data)
        if serializer.is_valid():
            user_role = serializer.save()
            return Response(UserRoleSerializer(user_role).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['User Roles'])
class UserRoleDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Remove a user role",
        description="Delete a specific user-role assignment",
        responses={204: None}
    )
    def delete(self, request, pk):
        user_role = get_object_or_404(UserRole, pk=pk)
        user_role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Role Groups'])
class RoleGroupListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all role groups",
        description="Get a list of all role groups in the system",
        responses={200: RoleGroupSerializer(many=True)}
    )
    def get(self, request):
        role_groups = RoleGroup.objects.all()  # type: ignore
        serializer = RoleGroupSerializer(role_groups, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create a new role group",
        description="Create a new role group with name, description and roles",
        request=RoleGroupCreateUpdateSerializer,
        responses={201: RoleGroupSerializer}
    )
    def post(self, request):
        serializer = RoleGroupCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            role_group = serializer.save()
            return Response(RoleGroupSerializer(role_group).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Role Groups'])
class RoleGroupDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get role group details",
        description="Get detailed information about a specific role group",
        responses={200: RoleGroupSerializer}
    )
    def get(self, request, pk):
        role_group = get_object_or_404(RoleGroup, pk=pk)
        serializer = RoleGroupSerializer(role_group)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update a role group",
        description="Update an existing role group's information",
        request=RoleGroupCreateUpdateSerializer,
        responses={200: RoleGroupSerializer}
    )
    def put(self, request, pk):
        role_group = get_object_or_404(RoleGroup, pk=pk)
        serializer = RoleGroupCreateUpdateSerializer(role_group, data=request.data)
        if serializer.is_valid():
            role_group = serializer.save()
            return Response(RoleGroupSerializer(role_group).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Delete a role group",
        description="Delete a specific role group from the system",
        responses={204: None}
    )
    def delete(self, request, pk):
        role_group = get_object_or_404(RoleGroup, pk=pk)
        role_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['User Roles'])
class UserRolesView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get user roles",
        description="Get all roles assigned to a specific user",
        responses={200: RoleSerializer(many=True)}
    )
    def get(self, request, user_id):
        """Get all roles for a specific user"""
        user = get_object_or_404(CustomUser, pk=user_id)
        user_roles = UserRole.objects.filter(user=user)  # type: ignore
        roles = [user_role.role for user_role in user_roles]
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)