from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from .models import Role, UserRole, RoleGroup

class RoleManagementTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=CustomUser.Role.ADMIN
        )
        
        # Create test permissions
        content_type = ContentType.objects.get_for_model(CustomUser)
        self.permission1 = Permission.objects.create(
            codename='can_view_data',
            name='Can View Data',
            content_type=content_type
        )
        self.permission2 = Permission.objects.create(
            codename='can_edit_data',
            name='Can Edit Data',
            content_type=content_type
        )
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def test_create_role(self):
        """Test creating a new role"""
        data = {
            'name': 'Test Role',
            'description': 'A test role',
            'permission_ids': [self.permission1.id, self.permission2.id],
            'is_active': True
        }
        
        response = self.client.post('/roles/roles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 1)
        self.assertEqual(Role.objects.get().name, 'Test Role')
        
        # Check that permissions were assigned
        role = Role.objects.get()
        self.assertTrue(role.has_permission(self.permission1))
        self.assertTrue(role.has_permission(self.permission2))
    
    def test_list_roles(self):
        """Test listing all roles"""
        # Create a role
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        role.permissions.add(self.permission1)
        
        response = self.client.get('/roles/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Role')
    
    def test_update_role(self):
        """Test updating a role"""
        # Create a role
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        
        # Update the role
        data = {
            'name': 'Updated Role',
            'description': 'An updated role',
            'permission_ids': [self.permission1.id],
            'is_active': False
        }
        
        response = self.client.put(f'/roles/roles/{role.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        role.refresh_from_db()
        self.assertEqual(role.name, 'Updated Role')
        self.assertEqual(role.description, 'An updated role')
        self.assertFalse(role.is_active)
        self.assertTrue(role.has_permission(self.permission1))
    
    def test_delete_role(self):
        """Test deleting a role"""
        # Create a role
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        
        response = self.client.delete(f'/roles/roles/{role.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.count(), 0)
    
    def test_assign_role_to_user(self):
        """Test assigning a role to a user"""
        # Create a role
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        
        # Assign role to user
        data = {
            'user': self.user.id,
            'role': role.id
        }
        
        response = self.client.post('/roles/user-roles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserRole.objects.count(), 1)
        
        user_role = UserRole.objects.get()
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, role)
        self.assertEqual(user_role.assigned_by, self.user)  # Assigned by self
    
    def test_list_user_roles(self):
        """Test listing user roles"""
        # Create a role and assign it to user
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        user_role = UserRole.objects.create(
            user=self.user,
            role=role,
            assigned_by=self.user
        )
        
        response = self.client.get('/roles/user-roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['id'], self.user.id)
        self.assertEqual(response.data[0]['role']['id'], role.id)
    
    def test_get_user_roles(self):
        """Test getting roles for a specific user"""
        # Create roles and assign them to user
        role1 = Role.objects.create(name='Role 1', description='First role')
        role2 = Role.objects.create(name='Role 2', description='Second role')
        
        UserRole.objects.create(user=self.user, role=role1, assigned_by=self.user)
        UserRole.objects.create(user=self.user, role=role2, assigned_by=self.user)
        
        response = self.client.get(f'/roles/users/{self.user.id}/roles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        role_names = [role['name'] for role in response.data]
        self.assertIn('Role 1', role_names)
        self.assertIn('Role 2', role_names)
    
    def test_create_role_group(self):
        """Test creating a role group"""
        # Create roles
        role1 = Role.objects.create(name='Role 1', description='First role')
        role2 = Role.objects.create(name='Role 2', description='Second role')
        
        # Create role group
        data = {
            'name': 'Test Group',
            'description': 'A test group',
            'role_ids': [role1.id, role2.id],
            'is_active': True
        }
        
        response = self.client.post('/roles/role-groups/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RoleGroup.objects.count(), 1)
        self.assertEqual(RoleGroup.objects.get().name, 'Test Group')
    
    def test_list_permissions(self):
        """Test listing all permissions"""
        response = self.client.get('/roles/permissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have at least the permissions we created
        self.assertGreaterEqual(len(response.data), 2)

class RoleModelTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=CustomUser.Role.ADMIN
        )
        
        # Create test permissions
        content_type = ContentType.objects.get_for_model(CustomUser)
        self.permission = Permission.objects.create(
            codename='can_view_data',
            name='Can View Data',
            content_type=content_type
        )
    
    def test_create_role(self):
        """Test creating a role"""
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        self.assertEqual(role.name, 'Test Role')
        self.assertEqual(role.description, 'A test role')
        self.assertTrue(role.is_active)
    
    def test_role_permissions(self):
        """Test role permission management"""
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        
        # Test adding permission
        role.add_permission(self.permission)
        self.assertTrue(role.has_permission(self.permission))
        
        # Test removing permission
        role.remove_permission(self.permission)
        self.assertFalse(role.has_permission(self.permission))
    
    def test_user_role_assignment(self):
        """Test user role assignment"""
        role = Role.objects.create(
            name='Test Role',
            description='A test role'
        )
        
        user_role = UserRole.objects.create(
            user=self.user,
            role=role,
            assigned_by=self.user
        )
        
        self.assertEqual(user_role.user, self.user)
        self.assertEqual(user_role.role, role)
        self.assertEqual(user_role.assigned_by, self.user)
    
    def test_role_group(self):
        """Test role group functionality"""
        # Create roles
        role1 = Role.objects.create(name='Role 1', description='First role')
        role2 = Role.objects.create(name='Role 2', description='Second role')
        
        # Create role group
        role_group = RoleGroup.objects.create(
            name='Test Group',
            description='A test group'
        )
        
        # Test adding roles to group
        role_group.add_role(role1)
        role_group.add_role(role2)
        
        self.assertEqual(role_group.roles.count(), 2)
        
        # Test removing role from group
        role_group.remove_role(role1)
        self.assertEqual(role_group.roles.count(), 1)
        self.assertEqual(role_group.roles.first(), role2)