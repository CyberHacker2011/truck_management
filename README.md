# Truck Management System

A comprehensive Django-based backend system for managing truck fleets, drivers, and delivery tasks with route optimization capabilities.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Models & Endpoints](#models--endpoints)
- [Frontend Integration Guide](#frontend-integration-guide)
- [Error Handling](#error-handling)
- [Development Guidelines](#development-guidelines)

## Features

- Multi-tenant architecture with company-based data isolation
- User role management (Company Admins, Drivers)
- Fleet management (Trucks, Drivers)
- Delivery task management and assignment
- Route optimization using OpenRouteService
- RESTful API with Django REST Framework
- JWT-based authentication
- Swagger/OpenAPI documentation
- Real-time driver location tracking
- Task start functionality for drivers

## Tech Stack

- Python 3.13
- Django 5.2
- Django REST Framework
- PostgreSQL
- JWT Authentication
- OpenRouteService API for routing
- Swagger/OpenAPI for API documentation

## Project Structure

```
truck_management/
├── core/                      # Main application directory
│   ├── models.py             # Data models
│   ├── views.py              # API views and endpoints
│   ├── serializers.py        # Model serializers
│   ├── urls.py               # URL routing
│   ├── admin.py              # Admin interface configuration
│   ├── maps_utils.py         # Map utility functions
│   ├── services/             # External service integrations
│   │   ├── google_maps.py    # Google Maps integration
│   │   └── openroute_service.py  # OpenRoute Service integration
│   └── management/           # Custom management commands
│       └── commands/
│           └── populate_sample_data.py  # Sample data population
└── truck_management/         # Project configuration
    ├── settings.py           # Project settings
    ├── urls.py              # Main URL configuration
    └── wsgi.py              # WSGI configuration
```

## Models

### Company

- Multi-tenant model for organization management
- Fields: name, created_at, updated_at

### Driver

- Represents truck drivers
- Fields: name, phone, license_number, experience_years, status
- Status options: available, on_mission

### Truck

- Represents vehicles in the fleet
- Fields: registration_number, model, capacity, fuel_type, status
- Status options: idle, in_use

### DeliveryTask

- Manages delivery assignments
- Fields: origin, destinations, assigned_driver, assigned_truck, status
- Includes route optimization capabilities

## API Endpoints

### Authentication

- POST /api/token/ - Obtain JWT token
- POST /api/token/refresh/ - Refresh JWT token

### Drivers

- GET /api/drivers/ - List drivers
- POST /api/drivers/ - Create driver
- GET /api/drivers/{id}/ - Retrieve driver
- PUT /api/drivers/{id}/ - Update driver
- DELETE /api/drivers/{id}/ - Delete driver
- GET /api/drivers/available/ - List available drivers

### Trucks

- GET /api/trucks/ - List trucks
- POST /api/trucks/ - Create truck
- GET /api/trucks/{id}/ - Retrieve truck
- PUT /api/trucks/{id}/ - Update truck
- DELETE /api/trucks/{id}/ - Delete truck
- GET /api/trucks/available/ - List available trucks

### Destinations

- GET /api/destinations/ - List destinations
- POST /api/destinations/ - Create destination
- GET /api/destinations/{id}/ - Retrieve destination
- PUT /api/destinations/{id}/ - Update destination
- DELETE /api/destinations/{id}/ - Delete destination

### Delivery Tasks

- GET /api/tasks/ - List delivery tasks
- POST /api/tasks/ - Create delivery task
- GET /api/tasks/{id}/ - Retrieve delivery task
- PUT /api/tasks/{id}/ - Update delivery task
- DELETE /api/tasks/{id}/ - Delete delivery task
- POST /api/tasks/{id}/start_task/ - Start a delivery task (driver only)
- POST /api/tasks/{id}/update_location/ - Update driver's location (driver only)
- POST /api/tasks/{id}/assign/ - Assign driver and truck
- GET /api/tasks/{id}/route/ - Get optimized route

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL
- Pipenv
- OpenRouteService API key

### Setup Instructions

1. Clone the repository

```bash
git clone <repository-url>
cd truck_management
```

2. Install dependencies using Pipenv

```bash
# Install Pipenv if you haven't
pip install pipenv

# Install project dependencies
pipenv install

# Activate the virtual environment
pipenv shell
```

3. Set up environment variables
   Create a `.env` file in the project root:

```env
DB_NAME=truckdb
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
OPENROUTE_API_KEY=your_openroute_api_key
```

4. Initialize the database

```bash
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser
```

5. Load sample data (optional)

```bash
pipenv run python manage.py populate_sample_data
```

6. Run the development server

```bash
pipenv run python manage.py runserver
```

## Frontend Integration Guide

### Setting Up API Client

1. **Install Axios or your preferred HTTP client**:

```bash
npm install axios
# or
yarn add axios
```

2. **Create API client with authentication**:

```javascript
// api/client.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response.status === 401) {
      // Try to refresh token
      const refresh = localStorage.getItem("refresh_token");
      try {
        const response = await axios.post("/api/token/refresh/", { refresh });
        localStorage.setItem("access_token", response.data.access);
        error.config.headers.Authorization = `Bearer ${response.data.access}`;
        return axios(error.config);
      } catch (refreshError) {
        // Redirect to login
        localStorage.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

3. **Example API calls**:

```javascript
// Authentication
const login = async (username, password) => {
  const response = await api.post("/token/", { username, password });
  localStorage.setItem("access_token", response.data.access);
  localStorage.setItem("refresh_token", response.data.refresh);
  return response.data;
};

// Fetch drivers
const getDrivers = async (status) => {
  const params = status ? { status } : {};
  const response = await api.get("/drivers/", { params });
  return response.data;
};

// Create delivery task
const createTask = async (taskData) => {
  const response = await api.post("/tasks/", taskData);
  return response.data;
};
```

## Error Handling

The API returns standardized error responses:

```javascript
{
    "error": string,
    "message": string,
    "details": object | null
}
```

Common HTTP status codes:

- 400: Bad Request (invalid data)
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

## Development Guidelines

### API Testing with Swagger

1. Visit http://localhost:8000/swagger/
2. Click "Authorize" and enter your Bearer token
3. Test endpoints directly from the Swagger UI

### Data Validation

All API endpoints perform validation. Common validation rules:

- Driver license numbers must be unique per company
- Phone numbers must be in valid format
- Experience years must be between 0 and 50
- Coordinates must be valid latitude/longitude values

