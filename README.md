# 🚛 Multi-Company Truck Management System

A Django-based backend system for managing truck fleets across multiple companies with role-based access control and JWT authentication.

## 🌟 Features

### Multi-Tenant Architecture

- **Company Separation**: Complete data isolation between companies
- **Role-Based Access**: Company Admin and Driver User roles
- **Secure Authentication**: JWT-based API authentication
- **PostgreSQL Database**: Production-ready database with proper constraints

### Core Functionality

- **Driver Management**: Track drivers with experience, status, and company assignment
- **Truck Fleet**: Manage trucks with capacity, fuel type, and availability
- **Delivery Tasks**: Assign and track delivery tasks across multiple destinations
- **Route Optimization**: Integration-ready for Google Maps and Yandex Maps APIs
- **Admin Panel**: Company-scoped Django admin interface

### API Endpoints

- **Authentication**: JWT token-based login system
- **Companies**: CRUD operations for company management
- **Drivers**: Company-scoped driver management
- **Trucks**: Fleet management with availability tracking
- **Destinations**: Delivery location management
- **Delivery Tasks**: Task assignment and status tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pipenv (recommended) or pip

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd truck_management
```

2. **Install dependencies**

```bash
pipenv install
# or
pip install -r requirements.txt
```

3. **Setup PostgreSQL database**

```sql
CREATE DATABASE truckdb;
CREATE USER postgres WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE truckdb TO postgres;
```

4. **Configure environment variables**
   Create `.env` file in `truck_management/` directory:

```env
DB_NAME=truckdb
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

5. **Run migrations**

```bash
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
```

6. **Create superuser**

```bash
pipenv run python manage.py createsuperuser
```

7. **Populate sample data**

```bash
pipenv run python manage.py populate_sample_data
```

8. **Start development server**

```bash
pipenv run python manage.py runserver
```

## 🔐 User Roles & Permissions

### Superuser

- Full access to all companies and data
- Can manage all system settings
- Access to Django admin panel

### Company Admin

- Manages only their assigned company's data
- Can create/edit drivers, trucks, destinations, and tasks
- Company-scoped API access
- Limited admin panel access

### Driver User

- Read-only access to their assigned tasks
- Can view task details and destinations
- Cannot create or modify data

## 🧪 Testing the System

### Sample Users Created

After running `populate_sample_data`, these test users are available:

**Company Admins:**

- `acme_admin` / `admin123` (Acme Logistics)
- `bolt_admin` / `admin123` (Bolt Transport)

**Driver Users:**

- `driver1` / `driver123`
- `driver2` / `driver123`
- `driver3` / `driver123`
- `driver4` / `driver123`

### API Testing

1. **Get JWT Token**

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "acme_admin", "password": "admin123"}'
```

2. **Access Company-Scoped Data**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/drivers/
```

3. **API Documentation**
   Visit: http://localhost:8000/api/docs/

## 📁 Project Structure

```
truck_management/
├── truck_management/          # Django project settings
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   └── .env                 # Environment variables
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # API viewsets
│   ├── serializers.py      # DRF serializers
│   ├── admin.py            # Django admin config
│   ├── urls.py             # API routing
│   ├── permissions.py      # Custom permissions
│   └── management/
│       └── commands/
│           └── populate_sample_data.py
└── README.md
```

## 🔧 API Endpoints

### Authentication

- `POST /api/auth/token/` - Get JWT access token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Core Resources

- `GET/POST /api/companies/` - Company management
- `GET/POST /api/drivers/` - Driver management
- `GET/POST /api/trucks/` - Truck fleet management
- `GET/POST /api/destinations/` - Delivery destinations
- `GET/POST /api/delivery-tasks/` - Task management

### Specialized Endpoints

- `GET /api/drivers/available/` - Available drivers only
- `GET /api/trucks/available/` - Available trucks only
- `GET /api/delivery-tasks/active/` - Active tasks only
- `POST /api/delivery-tasks/assign/` - Assign new task

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based API access
- **Company Data Isolation**: Users can only access their company's data
- **Role-Based Permissions**: Different access levels for different user types
- **Input Validation**: Comprehensive data validation and sanitization
- **CORS Configuration**: Proper cross-origin request handling

## 🗺️ Maps Integration Ready

The system is prepared for integration with:

- **Google Maps API**: Route calculation and optimization
- **Yandex Maps API**: Alternative mapping service
- **Geocoding Services**: Address to coordinates conversion
- **Reverse Geocoding**: Coordinates to address lookup

## 📊 Database Schema

### Core Models

- **Company**: Tenant/company information
- **CompanyAdmin**: Links Django User to Company
- **DriverUser**: Links Django User to Driver
- **Driver**: Driver information with company assignment
- **Truck**: Vehicle information with company assignment
- **Destination**: Delivery locations with company assignment
- **DeliveryTask**: Tasks linking drivers, trucks, and destinations

### Key Constraints

- Unique license numbers per company
- Unique plate numbers per company
- Foreign key relationships with CASCADE deletion
- Proper indexing for performance

## 🚀 Deployment Considerations

### Production Setup

1. Set `DEBUG = False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for sensitive data
4. Set up SSL certificates
5. Configure proper CORS origins
6. Use production PostgreSQL configuration
7. Set up proper logging and monitoring

### Environment Variables

```env
DB_NAME=production_db_name
DB_USER=production_user
DB_PASSWORD=secure_password
DB_HOST=production_host
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/api/docs/`
- Review the Django admin panel at `/admin/`

---

**Built with Django 5.2, Django REST Framework, and PostgreSQL**
