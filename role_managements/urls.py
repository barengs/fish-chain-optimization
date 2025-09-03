from django.urls import path
from . import views

urlpatterns = [
    # Role endpoints
    path('roles/', views.RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    
    # Permission endpoints
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    
    # User role endpoints
    path('user-roles/', views.UserRoleListView.as_view(), name='user-role-list'),
    path('user-roles/<int:pk>/', views.UserRoleDetailView.as_view(), name='user-role-detail'),
    path('users/<int:user_id>/roles/', views.UserRolesView.as_view(), name='user-roles'),
    
    # Role group endpoints
    path('role-groups/', views.RoleGroupListView.as_view(), name='role-group-list'),
    path('role-groups/<int:pk>/', views.RoleGroupDetailView.as_view(), name='role-group-detail'),
]