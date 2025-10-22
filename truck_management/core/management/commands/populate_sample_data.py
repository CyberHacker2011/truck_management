from django.core.management.base import BaseCommand
from core.models import Company, Driver, Truck, Destination, DeliveryTask
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create single company for testing
        company_a, _ = Company.objects.get_or_create(name='Acme Logistics')

        # Create one driver
        drivers_data = [
            {
                'name': 'John Smith',
                'phone': '+1-555-0101',
                'license_number': 'DL001234',
                'experience_years': 8,
                'status': 'available'
            },
        ]

        drivers = []
        for idx, driver_data in enumerate(drivers_data):
            driver_data['company'] = company_a
            driver, created = Driver.objects.get_or_create(
                company=driver_data['company'],
                license_number=driver_data['license_number'],
                defaults=driver_data
            )
            drivers.append(driver)
            if created:
                self.stdout.write(f'Created driver: {driver.name} ({driver.company.name})')

        # Create one truck
        trucks_data = [
            {
                'plate_number': 'TRK001',
                'model': 'Ford F-150',
                'capacity_kg': 1000,
                'fuel_type': 'diesel',
                'current_status': 'idle'
            }
        ]

        trucks = []
        for idx, truck_data in enumerate(trucks_data):
            truck_data['company'] = company_a
            truck, created = Truck.objects.get_or_create(
                company=truck_data['company'],
                plate_number=truck_data['plate_number'],
                defaults=truck_data
            )
            trucks.append(truck)
            if created:
                self.stdout.write(f'Created truck: {truck.model} ({truck.plate_number}) ({truck.company.name})')

        # Create destinations including base location
        destinations_data = [
            {
                'name': 'Acme Logistics Main Garage',
                'address': '100 Main St, Downtown, NY 10000',
                'latitude': Decimal('40.4494'),
                'longitude': Decimal('68.8049'),
                'is_base_location': True  # This is the base location
            },
            {
                'name': 'North Distribution Center',
                'address': '456 Commerce St, Uptown, NY 10002',
                'latitude': Decimal('40.3820'),
                'longitude': Decimal('68.7960'),
                'is_base_location': False
            },
            {
                'name': 'South Logistics Hub',
                'address': '789 Supply Ave, Midtown, NY 10003',
                'latitude': Decimal('40.4926'),
                'longitude': Decimal('68.8314'),
                'is_base_location': False
            },
            {
                'name': 'East Delivery Point',
                'address': '321 Delivery Rd, Eastside, NY 10004',
                'latitude': Decimal('40.4962'),
                'longitude': Decimal('68.7738'),
                'is_base_location': False
            }
        ]

        destinations = []
        for idx, dest_data in enumerate(destinations_data):
            dest_data['company'] = company_a
            destination, created = Destination.objects.get_or_create(
                company=dest_data['company'],
                name=dest_data['name'],
                defaults=dest_data
            )
            destinations.append(destination)
            if created:
                self.stdout.write(f'Created destination: {destination.name} ({destination.company.name})')

        # Create one task with delivery destinations (excluding base location)
        delivery_destinations = [d for d in destinations if not d.is_base_location]
        if drivers and trucks and len(delivery_destinations) >= 2:
            task, created = DeliveryTask.objects.get_or_create(
                company=company_a,
                driver=drivers[0],
                truck=trucks[0],
                product_name='Sample Goods',
                product_weight=500,
                status='assigned'
            )
            task.destinations.set(delivery_destinations[:3])  # Use first 3 delivery destinations
            if created:
                self.stdout.write(f'Created delivery task: {task.product_name} - {task.driver.name}')
                self.stdout.write(f'Task will route from base location to {len(delivery_destinations[:3])} destinations and back to base')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write(f'Created {len(drivers)} drivers, {len(trucks)} trucks, {len(destinations)} destinations, and 1 delivery task.')
