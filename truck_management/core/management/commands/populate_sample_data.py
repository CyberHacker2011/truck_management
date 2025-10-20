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

        # Create three destinations
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

        # Create one task with 3 destinations
        if drivers and trucks and len(destinations) >= 3:
            task, created = DeliveryTask.objects.get_or_create(
                company=company_a,
                driver=drivers[0],
                truck=trucks[0],
                product_name='Sample Goods',
                product_weight=500,
                status='assigned'
            )
            task.destinations.set(destinations[:3])
            if created:
                self.stdout.write(f'Created delivery task: {task.product_name} - {task.driver.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write(f'Created {len(drivers)} drivers, {len(trucks)} trucks, {len(destinations)} destinations, and 1 delivery task.')
