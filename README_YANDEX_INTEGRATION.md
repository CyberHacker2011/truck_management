# 🗺️ Yandex Maps Integration - Truck Management System

## Overview

This document describes the Yandex Maps API integration added to the Django truck management system. The integration provides automatic route generation for delivery tasks using Yandex's routing services.

## 🚀 Features Added

### 1. Enhanced Task Model
- **New Field**: `route_data` (JSONField) stores complete Yandex route information
- **Automatic Route Generation**: Routes are generated when tasks are created
- **Circular Route Support**: Start → Multiple Destinations → Return to Start

### 2. Yandex Maps Service
- **Geocoding**: Convert addresses to coordinates
- **Route Generation**: Build optimized circular routes
- **Error Handling**: Graceful fallback when API is unavailable
- **Company Isolation**: All routes are company-scoped

### 3. New API Endpoints
- `POST /api/tasks/create/` - Create task with automatic route generation
- `GET /api/tasks/<id>/` - Retrieve task with full route data

## 🔧 Technical Implementation

### Database Changes
```python
# Added to DeliveryTask model
route_data = models.JSONField(null=True, blank=True)
```

### Service Layer
```python
# core/services/yandex_map.py
class YandexMapService:
    def geocode(self, address: str) -> Dict[str, Any]
    def build_circular_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]
```

### API Integration
- **Automatic Route Generation**: Triggered during task creation
- **Error Resilience**: Tasks created even if routing fails
- **Company Scoping**: All operations respect multi-tenancy

## 📋 Setup Instructions

### 1. Environment Configuration
Add to your `.env` file:
```env
YANDEX_API_KEY=your_yandex_api_key_here
```

### 2. Install Dependencies
```bash
pip install requests
```

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Test Data Population
```bash
python manage.py populate_sample_data
```

## 🔑 API Usage

### Create Task with Route Generation
```bash
POST /api/tasks/create/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
    "driver": 1,
    "truck": 1,
    "destination_ids": [1, 2, 3],
    "product_name": "Electronics",
    "product_weight": 500,
    "status": "assigned"
}
```

**Response:**
```json
{
    "id": 1,
    "company": 1,
    "driver": 1,
    "truck": 1,
    "destinations": [1, 2, 3],
    "product_name": "Electronics",
    "product_weight": 500,
    "status": "assigned",
    "route_data": {
        "routes": [...],
        "total_distance": 15000,
        "total_duration": 1800
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}
```

### Retrieve Task with Route
```bash
GET /api/tasks/1/
Authorization: Bearer <jwt_token>
```

**Response includes full route data:**
```json
{
    "id": 1,
    "route_data": {
        "routes": [
            {
                "geometry": {
                    "coordinates": [[lon1, lat1], [lon2, lat2], ...]
                },
                "properties": {
                    "distance": 5000,
                    "duration": 600
                }
            }
        ],
        "total_distance": 15000,
        "total_duration": 1800
    }
}
```

## 🛡️ Security & Permissions

### Company Isolation
- All route generation respects company boundaries
- Users can only access routes for their company's tasks
- API keys are company-scoped (if implemented)

### Role-Based Access
- **Company Admins**: Can create tasks with route generation
- **Driver Users**: Can view their assigned tasks with routes
- **Unauthorized Users**: Cannot access route data

## 🧪 Testing

### Run API Tests
```bash
python manage.py test core.tests
```

### Test Coverage
- ✅ Yandex service error handling
- ✅ Task creation with route generation
- ✅ Company isolation
- ✅ Driver user access
- ✅ Validation logic
- ✅ Unauthorized access prevention

## 🔄 Route Generation Process

1. **Task Creation**: Manager creates task with driver, truck, destinations
2. **Coordinate Extraction**: System extracts lat/lng from destinations
3. **Yandex API Call**: Builds circular route (start → destinations → start)
4. **Route Storage**: Complete route JSON saved to `route_data` field
5. **Error Handling**: If routing fails, error info stored instead

## 📊 Route Data Structure

The `route_data` field contains:
```json
{
    "routes": [
        {
            "geometry": {
                "coordinates": [[lon, lat], ...],
                "type": "LineString"
            },
            "properties": {
                "distance": 5000,
                "duration": 600,
                "mode": "driving"
            }
        }
    ],
    "total_distance": 15000,
    "total_duration": 1800,
    "waypoints": [
        {"lat": 40.7589, "lon": -73.9851},
        {"lat": 40.7614, "lon": -73.9776}
    ]
}
```

## ⚠️ Error Handling

### API Key Missing
```json
{
    "error": "routing_failed",
    "message": "YANDEX_API_KEY is not configured"
}
```

### Network Issues
```json
{
    "error": "routing_failed", 
    "message": "Connection timeout"
}
```

### Invalid Coordinates
```json
{
    "error": "routing_failed",
    "message": "Invalid coordinate format"
}
```

## 🚀 Production Considerations

### Performance
- Route generation is asynchronous-friendly
- Consider background task processing for large datasets
- Implement caching for frequently used routes

### Monitoring
- Log route generation failures
- Monitor API usage and costs
- Track route optimization effectiveness

### Scaling
- Consider route pre-computation
- Implement route caching
- Use CDN for route data delivery

## 📈 Future Enhancements

1. **Route Optimization**: Implement TSP algorithms
2. **Real-time Updates**: Live route tracking
3. **Traffic Integration**: Real-time traffic data
4. **Multi-modal**: Public transport integration
5. **Route Comparison**: Multiple routing providers

## 🔗 Related Documentation

- [Yandex Maps API Documentation](https://yandex.com/dev/maps/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Built with Django 5.2, Django REST Framework, and Yandex Maps API**
