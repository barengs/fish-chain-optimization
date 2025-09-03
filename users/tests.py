from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import IndividualOwnerProfile, CompanyOwnerProfile, CaptainProfile

CustomUser = get_user_model()

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'admin',
            'password': 'testpass123',
            'password2': 'testpass123'
        }
    
    def test_register_user(self):
        response = self.client.post('/users/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().username, 'testuser')
    
    def test_register_user_with_mismatched_passwords(self):
        data = self.user_data.copy()
        data['password2'] = 'differentpassword'
        response = self.client.post('/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomUser.objects.count(), 0)
    
    def test_register_individual_owner(self):
        data = {
            'username': 'owneruser',
            'email': 'owner@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'owner_type': 'individual',
            'profile': {
                'first_name': 'John',
                'last_name': 'Doe',
                'id_number': '1234567890',
                'phone_number': '08123456789'
            }
        }
        response = self.client.post('/users/register/owner/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(IndividualOwnerProfile.objects.count(), 1)
    
    def test_register_company_owner(self):
        data = {
            'username': 'companyuser',
            'email': 'company@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'owner_type': 'company',
            'profile': {
                'company_name': 'Test Company',
                'company_registration_number': 'COMP12345',
                'tax_number': 'TAX12345',
                'contact_person': 'Jane Smith',
                'phone_number': '08123456789'
            }
        }
        response = self.client.post('/users/register/owner/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CompanyOwnerProfile.objects.count(), 1)
    
    def test_register_captain(self):
        data = {
            'username': 'captainuser',
            'email': 'captain@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'profile': {
                'first_name': 'Captain',
                'last_name': 'Jack',
                'license_number': 'LIC12345',
                'years_of_experience': 10,
                'phone_number': '08123456789'
            }
        }
        response = self.client.post('/users/register/captain/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CaptainProfile.objects.count(), 1)

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=CustomUser.Role.ADMIN
        )
    
    def test_create_user(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, CustomUser.Role.ADMIN)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_create_superuser(self):
        admin_user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
    
    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser (Admin)')

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role=CustomUser.Role.PEMILIK_KAPAL
        )
    
    def test_create_individual_owner_profile(self):
        profile = IndividualOwnerProfile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            id_number='1234567890'
        )
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.id_number, '1234567890')
        self.assertEqual(str(profile), 'John Doe')
    
    def test_create_company_owner_profile(self):
        profile = CompanyOwnerProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            company_registration_number='COMP12345',
            tax_number='TAX12345',
            contact_person='Jane Smith'
        )
        self.assertEqual(profile.company_name, 'Test Company')
        self.assertEqual(str(profile), 'Test Company')
    
    def test_create_captain_profile(self):
        profile = CaptainProfile.objects.create(
            user=self.user,
            first_name='Captain',
            last_name='Jack',
            license_number='LIC12345',
            years_of_experience=10
        )
        self.assertEqual(profile.first_name, 'Captain')
        self.assertEqual(profile.license_number, 'LIC12345')
        self.assertEqual(str(profile), 'Captain Jack (License: LIC12345)')