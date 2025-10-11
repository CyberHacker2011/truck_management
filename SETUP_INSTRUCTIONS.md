# Setup Instructions for Truck Management System

## Quick Setup (Windows)

### Option 1: Using the Setup Script
1. Double-click `setup.bat` to run the automated setup
2. Follow the prompts to create a superuser
3. Once complete, double-click `run_server.bat` to start the server

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pipenv install
   ```

2. **Navigate to Django Project**
   ```bash
   cd truck_management
   ```

3. **Create Migrations**
   ```bash
   pipenv run python manage.py makemigrations
   ```

4. **Run Migrations**
   ```bash
   pipenv run python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   pipenv run python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

6. **Populate Sample Data (Optional)**
   ```bash
   pipenv run python manage.py populate_sample_data
   ```

7. **Run Development Server**
   ```bash
   pipenv run python manage.py runserver
   ```

## Access Points

Once the server is running, you can access:

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc/

## Testing the API

### Using Browser
Navigate to http://localhost:8000/api/ to see all available endpoints.

### Using curl (Command Line)

**Get all drivers:**
```bash
curl http://localhost:8000/api/drivers/
```

**Get available drivers:**
```bash
curl http://localhost:8000/api/drivers/available/
```

**Create a new driver:**
```bash
curl -X POST http://localhost:8000/api/drivers/ ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test Driver\",\"phone\":\"+1234567890\",\"license_number\":\"DL999999\",\"experience_years\":5,\"status\":\"available\"}"
```

**Assign a delivery task:**
```bash
curl -X POST http://localhost:8000/api/delivery-tasks/assign/ ^
  -H "Content-Type: application/json" ^
  -d "{\"driver_id\":1,\"truck_id\":1,\"destination_ids\":[1,2],\"product_name\":\"Test Product\",\"product_weight\":500}"
```

## Project Structure

```
truck_management_project/
├── Pipfile                          # Python dependencies
├── Pipfile.lock                     # Locked dependencies
├── README.md                        # Main documentation
├── SETUP_INSTRUCTIONS.md           # This file
├── setup.bat                        # Windows setup script
├── run_server.bat                   # Windows run script
└── truck_management/                # Django project
    ├── manage.py                    # Django management script
    ├── db.sqlite3                   # SQLite database (created after migration)
    ├── core/                        # Main application
    │   ├── models.py               # Database models
    │   ├── serializers.py          # DRF serializers
    │   ├── views.py                # API views
    │   ├── admin.py                # Admin configuration
    │   ├── urls.py                 # API URLs
    │   ├── maps_utils.py           # Maps API utilities
    │   └── management/             # Management commands
    │       └── commands/
    │           └── populate_sample_data.py
    └── truck_management/            # Project settings
        ├── settings.py             # Django settings
        ├── urls.py                 # Main URL configuration
        └── wsgi.py                 # WSGI configuration
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"
**Solution**: Make sure you've installed dependencies with `pipenv install`

### Issue: "No such file or directory: manage.py"
**Solution**: Make sure you're in the `truck_management` directory

### Issue: "Port already in use"
**Solution**: Either stop the other process or run on a different port:
```bash
pipenv run python manage.py runserver 8001
```

### Issue: Dependencies not installing
**Solution**: Try updating pipenv:
```bash
pip install --upgrade pipenv
pipenv install --skip-lock
```

## Next Steps

1. Log in to the admin panel at http://localhost:8000/admin/
2. Explore the API at http://localhost:8000/api/
3. Read the API documentation at http://localhost:8000/api/docs/
4. Test the endpoints using the examples in README.md
5. Implement the Maps API integration in `core/maps_utils.py`

## Development Workflow

1. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

2. Make changes to your code

3. If you modify models, create and run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints Summary

### Drivers
- `GET /api/drivers/` - List all drivers
- `POST /api/drivers/` - Create driver
- `GET /api/drivers/{id}/` - Get driver details
- `PUT /api/drivers/{id}/` - Update driver
- `DELETE /api/drivers/{id}/` - Delete driver
- `GET /api/drivers/available/` - Get available drivers

### Trucks
- `GET /api/trucks/` - List all trucks
- `POST /api/trucks/` - Create truck
- `GET /api/trucks/{id}/` - Get truck details
- `PUT /api/trucks/{id}/` - Update truck
- `DELETE /api/trucks/{id}/` - Delete truck
- `GET /api/trucks/available/` - Get available trucks

### Destinations
- `GET /api/destinations/` - List all destinations
- `POST /api/destinations/` - Create destination
- `GET /api/destinations/{id}/` - Get destination details
- `PUT /api/destinations/{id}/` - Update destination
- `DELETE /api/destinations/{id}/` - Delete destination

### Delivery Tasks
- `GET /api/delivery-tasks/` - List all tasks
- `POST /api/delivery-tasks/` - Create task
- `GET /api/delivery-tasks/{id}/` - Get task details
- `PUT /api/delivery-tasks/{id}/` - Update task
- `DELETE /api/delivery-tasks/{id}/` - Delete task
- `POST /api/delivery-tasks/assign/` - Assign new task
- `POST /api/delivery-tasks/{id}/start/` - Start task
- `POST /api/delivery-tasks/{id}/complete/` - Complete task
- `GET /api/delivery-tasks/active/` - Get active tasks
- `POST /api/delivery-tasks/{id}/optimize_route/` - Optimize route

## Support

For issues or questions, refer to the main README.md file or Django documentation at https://docs.djangoproject.com/
