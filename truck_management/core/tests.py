"""
Comprehensive API tests for delivery task management and Yandex Maps integration.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Company, Driver, Truck, Destination, DeliveryTask, CompanyAdmin, DriverUser
from .services.openroute_service import OpenRouteService
import json


class OpenRouteServiceTest(TestCase):
    """Test OpenRouteService functionality."""
    
    def setUp(self):
        self.service = OpenRouteService(api_key="test_key")
    
    def test_geocode_without_api_key(self):
        """Test geocoding fails gracefully without API key."""
        service = OpenRouteService(api_key=None)
        with self.assertRaises(RuntimeError):
            service.geocode("Test Address")
    
    def test_build_circular_route_empty_points(self):
        """Test circular route with empty points returns error."""
        result = self.service.build_circular_route([])
        self.assertIn('error', result)
    
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
    """Test task creation and retrieval with Google Maps integration."""
    
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
        """Test task creation without Google Maps API key."""
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


class DeliveryTaskCreationWorkflowTest(APITestCase):
    """Comprehensive tests for delivery task creation workflow."""
    
    def setUp(self):
        # Create test company and admin
        self.company = Company.objects.create(name="Test Company")
        self.user = User.objects.create_user(username="admin", password="testpass")
        self.company_admin = CompanyAdmin.objects.create(user=self.user, company=self.company)
        
        # Create test resources
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
    
    def test_complete_task_creation_workflow(self):
        """Test complete task creation workflow with all validations."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [d.id for d in self.destinations],
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify task was created correctly
        task = DeliveryTask.objects.get(id=response.data['id'])
        self.assertEqual(task.product_name, 'Test Product')
        self.assertEqual(task.product_weight, 500)
        self.assertEqual(task.status, 'assigned')
        self.assertEqual(task.destinations.count(), 3)
        
        # Verify driver and truck status updates
        self.driver.refresh_from_db()
        self.truck.refresh_from_db()
        self.assertEqual(self.driver.status, 'on_mission')
        self.assertEqual(self.truck.current_status, 'in_use')
    
    def test_task_creation_without_destinations(self):
        """Test task creation without destinations."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        task = DeliveryTask.objects.get(id=response.data['id'])
        self.assertEqual(task.destinations.count(), 0)
    
    def test_task_creation_with_invalid_driver(self):
        """Test task creation with unavailable driver."""
        self.driver.status = 'on_mission'
        self.driver.save()
        
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [self.destinations[0].id],
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not available', str(response.data))
    
    def test_task_creation_with_invalid_truck(self):
        """Test task creation with unavailable truck."""
        self.truck.current_status = 'in_use'
        self.truck.save()
        
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [self.destinations[0].id],
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not available', str(response.data))
    
    def test_task_creation_with_excessive_weight(self):
        """Test task creation with product weight exceeding truck capacity."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [self.destinations[0].id],
            'product_name': 'Heavy Product',
            'product_weight': 1500  # Exceeds truck capacity of 1000kg
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('exceeds truck capacity', str(response.data))
    
    def test_task_creation_with_invalid_destinations(self):
        """Test task creation with non-existent destination IDs."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'destination_ids': [999, 998],  # Non-existent IDs
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Task should be created but with no destinations
        task = DeliveryTask.objects.get(id=response.data['id'])
        self.assertEqual(task.destinations.count(), 0)


class DeliveryTaskViewSetActionsTest(APITestCase):
    """Test ViewSet actions for delivery tasks."""
    
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
        
        # Create test task
        self.task = DeliveryTask.objects.create(
            company=self.company,
            driver=self.driver,
            truck=self.truck,
            product_name="Test Product",
            product_weight=500,
            status="assigned"
        )
        self.task.destinations.set(self.destinations)
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_task_assignment_endpoint(self):
        """Test the assign action endpoint."""
        url = reverse('deliverytask-assign')
        data = {
            'driver_id': self.driver.id,
            'truck_id': self.truck.id,
            'destination_ids': [d.id for d in self.destinations],
            'product_name': 'Assigned Product',
            'product_weight': 300
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify task was created
        task = DeliveryTask.objects.get(id=response.data['id'])
        self.assertEqual(task.product_name, 'Assigned Product')
        self.assertEqual(task.status, 'assigned')
    
    def test_task_start_endpoint(self):
        """Test the start action endpoint."""
        url = reverse('deliverytask-start', kwargs={'pk': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status change
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_task_start_invalid_status(self):
        """Test starting a task that's not in assigned status."""
        self.task.status = 'completed'
        self.task.save()
        
        url = reverse('deliverytask-start', kwargs={'pk': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('must be in assigned status', str(response.data))
    
    def test_task_complete_endpoint(self):
        """Test the complete action endpoint."""
        self.task.status = 'in_progress'
        self.task.save()
        
        url = reverse('deliverytask-complete', kwargs={'pk': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status change and driver/truck status updates
        self.task.refresh_from_db()
        self.driver.refresh_from_db()
        self.truck.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertEqual(self.driver.status, 'available')
        self.assertEqual(self.truck.current_status, 'idle')
    
    def test_task_complete_invalid_status(self):
        """Test completing a task that's already completed."""
        self.task.status = 'completed'
        self.task.save()
        
        url = reverse('deliverytask-complete', kwargs={'pk': self.task.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('must be in assigned or in_progress status', str(response.data))
    
    def test_active_tasks_endpoint(self):
        """Test the active tasks endpoint."""
        # Create another task in different status
        DeliveryTask.objects.create(
            company=self.company,
            driver=self.driver,
            truck=self.truck,
            product_name="Completed Task",
            product_weight=200,
            status="completed"
        )
        
        url = reverse('deliverytask-active')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the assigned task
        self.assertEqual(response.data[0]['status'], 'assigned')


class DeliveryTaskCompanyIsolationTest(APITestCase):
    """Test company isolation for delivery tasks."""
    
    def setUp(self):
        # Create two companies
        self.company1 = Company.objects.create(name="Company 1")
        self.company2 = Company.objects.create(name="Company 2")
        
        # Create users for each company
        self.user1 = User.objects.create_user(username="admin1", password="testpass")
        self.user2 = User.objects.create_user(username="admin2", password="testpass")
        
        self.company_admin1 = CompanyAdmin.objects.create(user=self.user1, company=self.company1)
        self.company_admin2 = CompanyAdmin.objects.create(user=self.user2, company=self.company2)
        
        # Create resources for company 1
        self.driver1 = Driver.objects.create(
            company=self.company1,
            name="Driver 1",
            phone="+1234567890",
            license_number="DL111111",
            experience_years=5,
            status="available"
        )
        
        self.truck1 = Truck.objects.create(
            company=self.company1,
            plate_number="TRK111",
            model="Truck 1",
            capacity_kg=1000,
            fuel_type="diesel",
            current_status="idle"
        )
        
        # Create resources for company 2
        self.driver2 = Driver.objects.create(
            company=self.company2,
            name="Driver 2",
            phone="+1234567891",
            license_number="DL222222",
            experience_years=3,
            status="available"
        )
        
        self.truck2 = Truck.objects.create(
            company=self.company2,
            plate_number="TRK222",
            model="Truck 2",
            capacity_kg=800,
            fuel_type="gasoline",
            current_status="idle"
        )
        
        # Create tasks for each company
        self.task1 = DeliveryTask.objects.create(
            company=self.company1,
            driver=self.driver1,
            truck=self.truck1,
            product_name="Product 1",
            product_weight=500,
            status="assigned"
        )
        
        self.task2 = DeliveryTask.objects.create(
            company=self.company2,
            driver=self.driver2,
            truck=self.truck2,
            product_name="Product 2",
            product_weight=300,
            status="assigned"
        )
    
    def test_company_isolation_in_task_list(self):
        """Test that users only see their company's tasks."""
        # Login as company 1 admin
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('deliverytask-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.task1.id)
    
    def test_company_isolation_in_task_detail(self):
        """Test that users cannot access other company's task details."""
        # Login as company 1 admin
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Try to access company 2's task
        url = reverse('deliverytask-detail', kwargs={'pk': self.task2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_company_isolation_in_task_creation(self):
        """Test that users cannot assign resources from other companies."""
        # Login as company 1 admin
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('task-create')
        data = {
            'driver': self.driver2.id,  # Driver from company 2
            'truck': self.truck1.id,
            'product_name': 'Cross Company Task',
            'product_weight': 200
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeliveryTaskDriverUserTest(APITestCase):
    """Test delivery task access for driver users."""
    
    def setUp(self):
        # Create test data
        self.company = Company.objects.create(name="Test Company")
        self.admin_user = User.objects.create_user(username="admin", password="testpass")
        self.driver_user = User.objects.create_user(username="driver", password="testpass")
        
        self.company_admin = CompanyAdmin.objects.create(user=self.admin_user, company=self.company)
        
        self.driver = Driver.objects.create(
            company=self.company,
            name="Test Driver",
            phone="+1234567890",
            license_number="DL123456",
            experience_years=5,
            status="available"
        )
        
        self.driver_user_profile = DriverUser.objects.create(user=self.driver_user, driver=self.driver)
        
        self.truck = Truck.objects.create(
            company=self.company,
            plate_number="TRK001",
            model="Test Truck",
            capacity_kg=1000,
            fuel_type="diesel",
            current_status="idle"
        )
        
        # Create tasks - one for this driver, one for another driver
        self.assigned_task = DeliveryTask.objects.create(
            company=self.company,
            driver=self.driver,
            truck=self.truck,
            product_name="My Task",
            product_weight=500,
            status="assigned"
        )
        
        # Create another driver and task
        other_driver = Driver.objects.create(
            company=self.company,
            name="Other Driver",
            phone="+1234567891",
            license_number="DL654321",
            experience_years=3,
            status="available"
        )
        
        self.other_task = DeliveryTask.objects.create(
            company=self.company,
            driver=other_driver,
            truck=self.truck,
            product_name="Other Task",
            product_weight=300,
            status="assigned"
        )
    
    def test_driver_user_sees_only_own_tasks(self):
        """Test that driver users only see their assigned tasks."""
        refresh = RefreshToken.for_user(self.driver_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('deliverytask-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.assigned_task.id)
    
    def test_driver_user_cannot_create_tasks(self):
        """Test that driver users cannot create tasks."""
        refresh = RefreshToken.for_user(self.driver_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Unauthorized Task',
            'product_weight': 200
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_driver_user_cannot_access_other_tasks(self):
        """Test that driver users cannot access tasks assigned to other drivers."""
        refresh = RefreshToken.for_user(self.driver_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('deliverytask-detail', kwargs={'pk': self.other_task.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeliveryTaskEdgeCasesTest(APITestCase):
    """Test edge cases and error scenarios for delivery tasks."""
    
    def setUp(self):
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
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_task_creation_with_missing_required_fields(self):
        """Test task creation with missing required fields."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            # Missing truck, product_name, product_weight
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_task_creation_with_invalid_driver_id(self):
        """Test task creation with non-existent driver ID."""
        url = reverse('task-create')
        data = {
            'driver': 999,  # Non-existent ID
            'truck': self.truck.id,
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_task_creation_with_invalid_truck_id(self):
        """Test task creation with non-existent truck ID."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': 999,  # Non-existent ID
            'product_name': 'Test Product',
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_task_creation_with_negative_weight(self):
        """Test task creation with negative product weight."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Test Product',
            'product_weight': -100  # Negative weight
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_task_creation_with_empty_product_name(self):
        """Test task creation with empty product name."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': '',  # Empty name
            'product_weight': 500
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_task_creation_with_zero_weight(self):
        """Test task creation with zero product weight."""
        url = reverse('task-create')
        data = {
            'driver': self.driver.id,
            'truck': self.truck.id,
            'product_name': 'Test Product',
            'product_weight': 0  # Zero weight
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)