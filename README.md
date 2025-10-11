# Truck Management System - Django Backend

A Django REST API backend for managing a logistics garage system with trucks, drivers, and delivery tasks.

## Features

- **Driver Management**: Track drivers with their license information and availability status
- **Truck Fleet**: Manage truck inventory with capacity and fuel type tracking
- **Destination Management**: Store delivery locations with GPS coordinates
- **Delivery Task Assignment**: Assign drivers and trucks to delivery tasks with multiple destinations
- **Route Optimization**: Placeholder functions for Google Maps and Yandex Maps API integration
- **REST API**: Full CRUD operations with filtering and search capabilities
- **Admin Interface**: Django admin with search and filters for all models

## Project Structure

```
truck_management/
├── truck_management/          # Main Django project
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── core/                     # Main application
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   ├── admin.py             # Django admin configuration
│   ├── maps_utils.py        # Maps API integration utilities
│   └── urls.py              # API URL routing
├── manage.py                 # Django management script
├── Pipfile                   # Python dependencies
└── README.md                 # This file
```

## Models

### Driver
- `name`: Driver's full name
- `phone`: Contact phone number
- `license_number`: Unique license number
- `experience_years`: Years of driving experience
- `status`: Available or on mission

### Truck
- `plate_number`: Unique license plate
- `model`: Truck model and make
- `capacity_kg`: Maximum cargo capacity
- `fuel_type`: Diesel, gasoline, electric, or hybrid
- `current_status`: Idle or in use

### Destination
- `name`: Destination name or business
- `address`: Full address
- `latitude`: GPS latitude coordinate
- `longitude`: GPS longitude coordinate

### DeliveryTask
- `driver`: Foreign key to Driver
- `truck`: Foreign key to Truck
- `destinations`: Many-to-many with Destination
- `product_name`: Product being delivered
- `product_weight`: Weight in kilograms
- `status`: Assigned, in progress, or completed

## API Endpoints

### Base URL: `/api/`

#### Drivers
- `GET /api/drivers/` - List all drivers
- `POST /api/drivers/` - Create new driver
- `GET /api/drivers/{id}/` - Get specific driver
- `PUT /api/drivers/{id}/` - Update driver
- `DELETE /api/drivers/{id}/` - Delete driver
- `GET /api/drivers/available/` - Get available drivers
- `GET /api/drivers/?status=available` - Filter by status

#### Trucks
- `GET /api/trucks/` - List all trucks
- `POST /api/trucks/` - Create new truck
- `GET /api/trucks/{id}/` - Get specific truck
- `PUT /api/trucks/{id}/` - Update truck
- `DELETE /api/trucks/{id}/` - Delete truck
- `GET /api/trucks/available/` - Get available trucks
- `GET /api/trucks/?status=idle&fuel_type=diesel` - Filter trucks

#### Destinations
- `GET /api/destinations/` - List all destinations
- `POST /api/destinations/` - Create new destination
- `GET /api/destinations/{id}/` - Get specific destination
- `PUT /api/destinations/{id}/` - Update destination
- `DELETE /api/destinations/{id}/` - Delete destination
- `GET /api/destinations/?search=warehouse` - Search destinations

#### Delivery Tasks
- `GET /api/delivery-tasks/` - List all tasks
- `POST /api/delivery-tasks/` - Create new task
- `GET /api/delivery-tasks/{id}/` - Get specific task
- `PUT /api/delivery-tasks/{id}/` - Update task
- `DELETE /api/delivery-tasks/{id}/` - Delete task
- `POST /api/delivery-tasks/assign/` - Assign new task
- `POST /api/delivery-tasks/{id}/start/` - Start task
- `POST /api/delivery-tasks/{id}/complete/` - Complete task
- `GET /api/delivery-tasks/active/` - Get active tasks
- `POST /api/delivery-tasks/{id}/optimize_route/` - Optimize route for task
- `POST /api/delivery-tasks/calculate_route/` - Calculate route between destinations
- `POST /api/delivery-tasks/geocode_address/` - Get coordinates for address
- `POST /api/delivery-tasks/reverse_geocode/` - Get address for coordinates

## Setup Instructions

### Prerequisites
- Python 3.13
- pipenv

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Activate the virtual environment**
   ```bash
   pipenv shell
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser for admin access**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Access Points

- **API**: http://localhost:8000/api/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **Alternative API Docs**: http://localhost:8000/api/redoc/

## API Usage Examples

### Create a Driver
```bash
curl -X POST http://localhost:8000/api/drivers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+1234567890",
    "license_number": "DL123456",
    "experience_years": 5,
    "status": "available"
  }'
```

### Create a Truck
```bash
curl -X POST http://localhost:8000/api/trucks/ \
  -H "Content-Type: application/json" \
  -d '{
    "plate_number": "TRK001",
    "model": "Ford F-150",
    "capacity_kg": 1000,
    "fuel_type": "diesel",
    "current_status": "idle"
  }'
```

### Create a Destination
```bash
curl -X POST http://localhost:8000/api/destinations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Warehouse A",
    "address": "123 Industrial St, City, State",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### Assign a Delivery Task
```bash
curl -X POST http://localhost:8000/api/delivery-tasks/assign/ \
  -H "Content-Type: application/json" \
  -d '{
    "driver_id": 1,
    "truck_id": 1,
    "destination_ids": [1, 2, 3],
    "product_name": "Electronics",
    "product_weight": 500
  }'
```

### Get Available Drivers
```bash
curl http://localhost:8000/api/drivers/available/
```

### Get Active Tasks
```bash
curl http://localhost:8000/api/delivery-tasks/active/
```

## Maps API Integration

The system includes placeholder functions for integrating with external maps APIs:

### Google Maps Integration
- Route calculation and optimization
- Distance matrix calculation
- Geocoding and reverse geocoding

### Yandex Maps Integration
- Alternative maps provider support
- Route optimization algorithms
- Distance calculations

### Usage
To use the maps functionality, you'll need to:
1. Obtain API keys from Google Maps or Yandex Maps
2. Implement the actual API calls in the `maps_utils.py` file
3. Configure the API keys in your environment or settings

## Database

The project uses SQLite by default for development. To use a different database:

1. Update the `DATABASES` setting in `settings.py`
2. Install the appropriate database adapter
3. Run migrations

## Admin Interface

The Django admin interface provides:
- Full CRUD operations for all models
- Search functionality
- Filtering options
- Optimized queries with select_related and prefetch_related

Access the admin at http://localhost:8000/admin/ after creating a superuser.

## Development Notes

- All models include automatic timestamps (created_at, updated_at)
- Status updates are handled automatically when tasks are assigned/completed
- The system validates driver and truck availability before assignment
- Product weight is validated against truck capacity
- Coordinate validation ensures valid latitude/longitude values

## Future Enhancements

- Implement actual maps API integration
- Add authentication and permissions
- Implement real-time tracking
- Add notification system
- Create mobile app endpoints
- Add reporting and analytics
- Implement task scheduling
- Add fuel consumption tracking
