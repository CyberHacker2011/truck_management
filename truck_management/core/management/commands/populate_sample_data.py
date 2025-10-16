from django.core.management.base import BaseCommand
from core.models import Company, Driver, Truck, Destination, DeliveryTask
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create companies
        company_a, _ = Company.objects.get_or_create(name='Acme Logistics')
        company_b, _ = Company.objects.get_or_create(name='Bolt Transport')

        # Create sample drivers
        drivers_data = [
            {
                'name': 'John Smith',
                'phone': '+1-555-0101',
                'license_number': 'DL001234',
                'experience_years': 8,
                'status': 'available'
            },
            {
                'name': 'Sarah Johnson',
                'phone': '+1-555-0102',
                'license_number': 'DL001235',
                'experience_years': 5,
                'status': 'available'
            },
            {
                'name': 'Mike Wilson',
                'phone': '+1-555-0103',
                'license_number': 'DL001236',
                'experience_years': 12,
                'status': 'available'
            },
            {
                'name': 'Lisa Brown',
                'phone': '+1-555-0104',
                'license_number': 'DL001237',
                'experience_years': 3,
                'status': 'available'
            }
        ]

        drivers = []
        for idx, driver_data in enumerate(drivers_data):
            driver_data['company'] = company_a if idx % 2 == 0 else company_b
            driver, created = Driver.objects.get_or_create(
                company=driver_data['company'],
                license_number=driver_data['license_number'],
                defaults=driver_data
            )
            drivers.append(driver)
            if created:
                self.stdout.write(f'Created driver: {driver.name} ({driver.company.name})')

        # Create sample trucks
        trucks_data = [
            {
                'plate_number': 'TRK001',
                'model': 'Ford F-150',
                'capacity_kg': 1000,
                'fuel_type': 'diesel',
                'current_status': 'idle'
            },
            {
                'plate_number': 'TRK002',
                'model': 'Chevrolet Silverado',
                'capacity_kg': 1500,
                'fuel_type': 'diesel',
                'current_status': 'idle'
            },
            {
                'plate_number': 'TRK003',
                'model': 'Tesla Semi',
                'capacity_kg': 2000,
                'fuel_type': 'electric',
                'current_status': 'idle'
            },
            {
                'plate_number': 'TRK004',
                'model': 'Toyota Tacoma',
                'capacity_kg': 800,
                'fuel_type': 'gasoline',
                'current_status': 'idle'
            }
        ]

        trucks = []
        for idx, truck_data in enumerate(trucks_data):
            truck_data['company'] = company_a if idx % 2 == 0 else company_b
            truck, created = Truck.objects.get_or_create(
                company=truck_data['company'],
                plate_number=truck_data['plate_number'],
                defaults=truck_data
            )
            trucks.append(truck)
            if created:
                self.stdout.write(f'Created truck: {truck.model} ({truck.plate_number}) ({truck.company.name})')

        # Create sample destinations
        destinations_data = [
            {
                'name': 'Central Warehouse',
                'address': '123 Industrial Blvd, Downtown, NY 10001',
                'latitude': Decimal('40.7589'),
                'longitude': Decimal('-73.9851')
            },
            {
                'name': 'North Distribution Center',
                'address': '456 Commerce St, Uptown, NY 10002',
                'latitude': Decimal('40.7614'),
                'longitude': Decimal('-73.9776')
            },
            {
                'name': 'South Logistics Hub',
                'address': '789 Supply Ave, Midtown, NY 10003',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-73.9934')
            },
            {
                'name': 'East Storage Facility',
                'address': '321 Depot Rd, East Side, NY 10004',
                'latitude': Decimal('40.7282'),
                'longitude': Decimal('-73.7949')
            },
            {
                'name': 'West Fulfillment Center',
                'address': '654 Delivery St, West Side, NY 10005',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-74.0014')
            }
        ]

        destinations = []
        for idx, dest_data in enumerate(destinations_data):
            dest_data['company'] = company_a if idx % 2 == 0 else company_b
            destination, created = Destination.objects.get_or_create(
                company=dest_data['company'],
                name=dest_data['name'],
                defaults=dest_data
            )
            destinations.append(destination)
            if created:
                self.stdout.write(f'Created destination: {destination.name} ({destination.company.name})')

        # Create sample delivery tasks
        tasks_data = [
            {
                'company': company_a,
                'driver': drivers[0],
                'truck': trucks[0],
                'destinations': [destinations[0], destinations[1]],
                'product_name': 'Electronics Components',
                'product_weight': 500,
                'status': 'assigned'
            },
            {
                'company': company_b,
                'driver': drivers[1],
                'truck': trucks[1],
                'destinations': [destinations[2], destinations[3]],
                'product_name': 'Furniture Parts',
                'product_weight': 800,
                'status': 'assigned'
            }
        ]

        for task_data in tasks_data:
            destinations_list = task_data.pop('destinations')
            task, created = DeliveryTask.objects.get_or_create(
                company=task_data['company'],
                driver=task_data['driver'],
                truck=task_data['truck'],
                product_name=task_data['product_name'],
                defaults=task_data
            )
            if created:
                task.destinations.set(destinations_list)
                self.stdout.write(f'Created delivery task: {task.product_name} - {task.driver.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write(f'Created {len(drivers)} drivers, {len(trucks)} trucks, {len(destinations)} destinations, and {len(tasks_data)} delivery tasks.')
