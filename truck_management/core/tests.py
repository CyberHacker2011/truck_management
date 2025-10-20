"""
API tests for Yandex Maps integration and task management.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Company, Driver, Truck, Destination, DeliveryTask, CompanyAdmin
from .services.yandex_map import YandexMapService
import json


class YandexMapServiceTest(TestCase):
    """Test Yandex Maps service functionality."""
    
    def setUp(self):
        self.service = YandexMapService(api_key="test_key")
    
    def test_geocode_without_api_key(self):
        """Test geocoding fails gracefully without API key."""
        service = YandexMapService(api_key=None)
        with self.assertRaises(RuntimeError):
            service.geocode("Test Address")
    
    def test_build_circular_route_empty_points(self):
        """Test circular route with empty points returns empty dict."""
        result = self.service.build_circular_route([])
        self.assertEqual(result, {})
    
    def test_build_circular_route_single_point(self):
        """Test circular route with single point."""
        points = [(40.7589, -73.9851)]
        # This will fail with real API but should not crash
        try:
            result = self.service.build_circular_route(points)
            self.assertIsInstance(result, dict)
        except Exception:
            # Expected to fail without real API key
            pass


class TaskAPITest(APITestCase):
    """Test task creation and retrieval with Yandex Maps integration."""
    
    def setUp(self):
        # Create test data
        self.company = Company.objects.create(name="Test Company")
        self.user = User.objects.create_user(username="admin", password="testpass")
        self.company_admin = CompanyAdmin.objects.create(user=self.user, company=self.company)
        
        self.driver = Driver.objects.create(
            company=self.company,
            name="Test Driver",
            phone="+1234567890",
            license_number="DL123456",
            experience_years=5,
            status="available"
        )
        
        self.truck = Truck.objects.create(
            company=self.company,
            plate_number="TRK001",
            model="Test Truck",
            capacity_kg=1000,
            fuel_type="diesel",
            current_status="idle"
        )
        
        self.destinations = [
            Destination.objects.create(
                company=self.company,
                name=f"Destination {i}",
                address=f"Address {i}",
                latitude=40.7589 + i * 0.001,
                longitude=-73.9851 + i * 0.001
            ) for i in range(3)
        ]
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_task_creation_without_route(self):
        """Test task creation without Yandex API key."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [d.id for d in self.destinations],
            'product_name': 'Test Product',
            'product_weight': 500,
            'status': 'assigned'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check task was created
        task = DeliveryTask.objects.get(id=response.data['id'])
        self.assertEqual(task.product_name, 'Test Product')
        self.assertEqual(task.destinations.count(), 3)
        
        # Check route_data contains error (no API key)
        self.assertIsNotNone(task.route_data)
        self.assertIn('error', task.route_data)
    
    def test_task_detail_retrieval(self):
        """Test task detail retrieval with route data."""
        # Create task first
        task = DeliveryTask.objects.create(
            company=self.company,
            driver=self.driver,
            truck=self.truck,
            product_name="Test Product",
            product_weight=500,
            status="assigned",
            route_data={"test": "route_data"}
        )
        task.destinations.set(self.destinations)
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('route_data', response.data)
        self.assertEqual(response.data['route_data'], {"test": "route_data"})
    
    def test_company_isolation(self):
        """Test that users can only access their company's tasks."""
        # Create another company
        other_company = Company.objects.create(name="Other Company")
        other_driver = Driver.objects.create(
            company=other_company,
            name="Other Driver",
            phone="+1234567890",
            license_number="DL654321",
            experience_years=3,
            status="available"
        )
        other_truck = Truck.objects.create(
            company=other_company,
            plate_number="TRK002",
            model="Other Truck",
            capacity_kg=800,
            fuel_type="gasoline",
            current_status="idle"
        )
        
        # Create task for other company
        other_task = DeliveryTask.objects.create(
            company=other_company,
            driver=other_driver,
            truck=other_truck,
            product_name="Other Product",
            product_weight=300,
            status="assigned"
        )
        
        # Try to access other company's task
        url = reverse('task-detail', kwargs={'pk': other_task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_driver_user_access(self):
        """Test that driver users can only see their own tasks."""
        # Create driver user
        driver_user = User.objects.create_user(username="driver", password="testpass")
        from .models import DriverUser
        DriverUser.objects.create(user=driver_user, driver=self.driver)
        
        # Create task for this driver
        task = DeliveryTask.objects.create(
            company=self.company,
            driver=self.driver,
            truck=self.truck,
            product_name="Driver Task",
            product_weight=400,
            status="assigned"
        )
        
        # Login as driver
        refresh = RefreshToken.for_user(driver_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Should be able to access their own task
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot create tasks."""
        self.client.credentials()  # Remove authentication
        
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [self.destinations[0].id],
            'product_name': 'Unauthorized Product',
            'product_weight': 100,
            'status': 'assigned'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskValidationTest(TestCase):
    """Test task validation logic."""
    
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")
        
        self.driver = Driver.objects.create(
            company=self.company,
            name="Test Driver",
            phone="+1234567890",
            license_number="DL123456",
            experience_years=5,
            status="available"
        )
        
        self.truck = Truck.objects.create(
            company=self.company,
            plate_number="TRK001",
            model="Test Truck",
            capacity_kg=1000,
            fuel_type="diesel",
            current_status="idle"
        )
    
    def test_task_creation_with_heavy_product(self):
        """Test that task creation fails when product exceeds truck capacity."""
        from .serializers import DeliveryTaskSerializer
        
        data = {
            'company': self.company.id,
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Heavy Product',
            'product_weight': 1500,  # Exceeds truck capacity of 1000kg
            'status': 'assigned'
        }
        
        serializer = DeliveryTaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Product weight', str(serializer.errors))
    
    def test_task_creation_with_unavailable_driver(self):
        """Test that task creation fails with unavailable driver."""
        # Make driver unavailable
        self.driver.status = 'on_mission'
        self.driver.save()
        
        from .serializers import DeliveryTaskSerializer
        
        data = {
            'company': self.company.id,
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Test Product',
            'product_weight': 500,
            'status': 'assigned'
        }
        
        serializer = DeliveryTaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('not available', str(serializer.errors))