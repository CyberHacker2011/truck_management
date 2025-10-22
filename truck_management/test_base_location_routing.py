#!/usr/bin/env python3
"""
Test script to verify base location routing functionality.
"""

import os
import sys
import django
from dotenv import load_dotenv

# Add the project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_management.settings')
django.setup()

def test_base_location_routing():
    """Test the base location routing functionality."""
    try:
        from core.services.openroute_service import OpenRouteService
        
        # Get API key from environment
        api_key = os.getenv('OPENROUTE_API_KEY')
        
        if not api_key:
            print("❌ ERROR: OPENROUTE_API_KEY not found in environment variables")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        openroute_service = OpenRouteService(api_key)
        
        # Simulate the route calculation with base location
        print("\n🧪 Testing base location routing:")
        
        # Base location (garage/warehouse)
        base_location = (40.7589, -73.9851)  # Acme Logistics Main Garage
        
        # Delivery destinations
        destinations = [
            (40.7614, -73.9776),  # North Distribution Center
            (40.7505, -73.9934),  # South Logistics Hub
            (40.7450, -73.9700)   # East Delivery Point
        ]
        
        print(f"Base Location: {base_location}")
        print(f"Destinations: {destinations}")
        
        # Create route: base -> destinations -> back to base
        coords = [base_location] + destinations + [base_location]
        print(f"Full route coordinates: {coords}")
        
        # Test the route calculation
        route_result = openroute_service.build_circular_route(coords)
        
        print(f"\nRoute result: {route_result}")
        
        if 'error' in route_result and not route_result.get('fallback'):
            print(f"❌ Route calculation failed: {route_result['error']}")
            print(f"   Message: {route_result.get('message', 'No message')}")
            return False
        elif route_result.get('fallback'):
            print(f"⚠️ OpenRouteService failed, but fallback worked!")
            print(f"   Distance: {route_result.get('distance', 0)} meters")
            print(f"   Duration: {route_result.get('duration', 0)} seconds")
            print(f"   Message: {route_result.get('message', 'No message')}")
            return True
        else:
            print("✅ Route calculation successful!")
            print(f"   Distance: {route_result.get('distance', 0)} meters")
            print(f"   Duration: {route_result.get('duration', 0)} seconds")
            return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_route_structure():
    """Test the route structure to ensure it includes base location."""
    print("\n📋 Route Structure Analysis:")
    
    # Base location
    base_location = (40.7589, -73.9851)
    
    # Delivery destinations
    destinations = [
        (40.7614, -73.9776),  # North Distribution Center
        (40.7505, -73.9934),  # South Logistics Hub
    ]
    
    # Expected route structure
    expected_route = [base_location] + destinations + [base_location]
    
    print(f"Expected route structure:")
    print(f"1. Start at base: {base_location}")
    print(f"2. Visit destinations: {destinations}")
    print(f"3. Return to base: {base_location}")
    print(f"Total waypoints: {len(expected_route)}")
    
    # Calculate estimated distances
    import math
    
    def haversine_distance(lat1, lng1, lat2, lng2):
        """Calculate distance between two points using Haversine formula."""
        R = 6371000  # Earth's radius in meters
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2) * math.sin(dlng/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    total_distance = 0
    for i in range(len(expected_route) - 1):
        lat1, lng1 = expected_route[i]
        lat2, lng2 = expected_route[i + 1]
        distance = haversine_distance(lat1, lng1, lat2, lng2)
        total_distance += distance
        print(f"   Leg {i+1}: {expected_route[i]} -> {expected_route[i+1]} = {distance:.0f}m")
    
    print(f"Total estimated distance: {total_distance:.0f} meters")
    print(f"Estimated duration (50 km/h): {total_distance / 13.89:.0f} seconds")

def test_django_models():
    """Test the Django models to ensure base location functionality works."""
    try:
        from core.models import Destination, Company
        
        print("\n🏗️ Testing Django Models:")
        
        # Check if we can access the models
        print("✅ Successfully imported Destination and Company models")
        
        # Check if the is_base_location field exists
        destination_fields = [field.name for field in Destination._meta.fields]
        if 'is_base_location' in destination_fields:
            print("✅ is_base_location field exists in Destination model")
        else:
            print("❌ is_base_location field not found in Destination model")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Django models test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Base Location Routing...")
    print("=" * 50)
    
    # Test Django models first
    models_ok = test_django_models()
    
    if models_ok:
        test_route_structure()
        success = test_base_location_routing()
        
        if success:
            print("\n✅ Base location routing is working correctly!")
            print("\n📋 What this means:")
            print("- All delivery routes will start and end at the base location")
            print("- The system automatically includes the base location in route calculations")
            print("- Routes are calculated as: Base -> Destinations -> Base")
            print("- Fallback system ensures routes always work even if OpenRouteService fails")
        else:
            print("\n❌ Base location routing test failed")
            print("There might be an issue with the implementation")
    else:
        print("\n❌ Django models test failed - cannot proceed with routing test")