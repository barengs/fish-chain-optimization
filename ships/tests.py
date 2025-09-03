from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import OwnerProfile, CaptainProfile
from .models import Ship, ShipMaintenance, MaintenanceType

CustomUser = get_user_model()

class ShipAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.owner_user = CustomUser.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.captain_user = CustomUser.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='testpass123'
        )
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create owner profile
        self.owner_profile = OwnerProfile.objects.create(
            user=self.owner_user,
            type_owner='individual',
            first_name='John',
            last_name='Doe',
            id_number='1234567890',
            phone_number='08123456789'
        )
        
        # Create captain profile
        self.captain_profile = CaptainProfile.objects.create(
            user=self.captain_user,
            first_name='Captain',
            last_name='Jack',
            license_number='LIC12345',
            years_of_experience=10,
            phone_number='08123456789'
        )
        
        # Create a ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='TS12345',
            owner=self.owner_profile,
            captain=self.captain_profile,
            length=20.5,
            width=5.2,
            gross_tonnage=100.5,
            year_built=2020,
            home_port='Port City',
            active=True
        )
    
    def test_list_ships(self):
        """Test listing all ships"""
        response = self.client.get('/ships/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/ships/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_ship_detail(self):
        """Test getting ship details"""
        response = self.client.get(f'/ships/{self.ship.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/ships/{self.ship.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Ship')
    
    def test_create_ship(self):
        """Test creating a new ship"""
        data = {
            'name': 'New Ship',
            'registration_number': 'NS54321',
            'owner_id': self.owner_profile.id,
            'captain_id': self.captain_profile.id,
            'length': 25.0,
            'width': 6.0,
            'gross_tonnage': 150.0,
            'year_built': 2021,
            'home_port': 'New Port',
            'active': True
        }
        
        response = self.client.post('/ships/create/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/ships/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Ship')
    
    def test_update_ship(self):
        """Test updating a ship"""
        data = {
            'name': 'Updated Ship',
            'registration_number': 'TS12345',
            'owner_id': self.owner_profile.id,
            'captain_id': self.captain_profile.id,
            'length': 22.0,
            'width': 5.5,
            'gross_tonnage': 120.0,
            'year_built': 2020,
            'home_port': 'Updated Port',
            'active': True
        }
        
        response = self.client.put(f'/ships/{self.ship.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(f'/ships/{self.ship.id}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Ship')
    
    def test_delete_ship(self):
        """Test deleting a ship"""
        response = self.client.delete(f'/ships/{self.ship.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/ships/{self.ship.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify ship is deleted
        response = self.client.get(f'/ships/{self.ship.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ShipMaintenanceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.owner_user = CustomUser.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.captain_user = CustomUser.objects.create_user(
            username='captain',
            email='captain@example.com',
            password='testpass123'
        )
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        
        # Create owner profile
        self.owner_profile = OwnerProfile.objects.create(
            user=self.owner_user,
            type_owner='individual',
            first_name='John',
            last_name='Doe',
            id_number='1234567890',
            phone_number='08123456789'
        )
        
        # Create captain profile
        self.captain_profile = CaptainProfile.objects.create(
            user=self.captain_user,
            first_name='Captain',
            last_name='Jack',
            license_number='LIC12345',
            years_of_experience=10,
            phone_number='08123456789'
        )
        
        # Create a ship
        self.ship = Ship.objects.create(
            name='Test Ship',
            registration_number='TS12345',
            owner=self.owner_profile,
            captain=self.captain_profile,
            length=20.5,
            width=5.2,
            gross_tonnage=100.5,
            year_built=2020,
            home_port='Port City',
            active=True
        )
        
        # Create a maintenance record
        self.maintenance = ShipMaintenance.objects.create(
            ship=self.ship,
            maintenance_type=MaintenanceType.ROUTINE,
            description='Regular engine maintenance',
            cost=500.00,
            performed_by='Marine Services Inc.',
            date_performed='2023-01-15',
            next_due_date='2023-07-15'
        )
    
    def test_list_maintenance_records(self):
        """Test listing all maintenance records"""
        response = self.client.get('/ships/maintenance/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/ships/maintenance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_maintenance_record_detail(self):
        """Test getting maintenance record details"""
        response = self.client.get(f'/ships/maintenance/{self.maintenance.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/ships/maintenance/{self.maintenance.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Regular engine maintenance')
    
    def test_create_maintenance_record(self):
        """Test creating a new maintenance record"""
        data = {
            'ship_id': self.ship.id,
            'maintenance_type': MaintenanceType.REPAIR,
            'description': 'Fixed engine problem',
            'cost': 1200.00,
            'performed_by': 'Expert Mechanics',
            'date_performed': '2023-02-20',
            'next_due_date': '2023-08-20'
        }
        
        response = self.client.post('/ships/maintenance/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/ships/maintenance/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], 'Fixed engine problem')
    
    def test_update_maintenance_record(self):
        """Test updating a maintenance record"""
        data = {
            'ship_id': self.ship.id,
            'maintenance_type': MaintenanceType.REPAIR,
            'description': 'Updated engine repair',
            'cost': 1500.00,
            'performed_by': 'Expert Mechanics',
            'date_performed': '2023-02-20',
            'next_due_date': '2023-08-20'
        }
        
        response = self.client.put(f'/ships/maintenance/{self.maintenance.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(f'/ships/maintenance/{self.maintenance.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated engine repair')
        self.assertEqual(float(response.data['cost']), 1500.00)
    
    def test_delete_maintenance_record(self):
        """Test deleting a maintenance record"""
        response = self.client.delete(f'/ships/maintenance/{self.maintenance.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/ships/maintenance/{self.maintenance.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify maintenance record is deleted
        response = self.client.get(f'/ships/maintenance/{self.maintenance.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)