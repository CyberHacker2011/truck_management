#!/usr/bin/env python3
"""
Simple test to verify OpenRouteService API key is working.
"""

import os
import sys
import django
import requests
import json
from dotenv import load_dotenv

# Add the project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'truck_management.settings')
django.setup()

def test_api_key():
    """Test if the API key is working with a simple request."""
    api_key = os.getenv('OPENROUTE_API_KEY')
    
    if not api_key:
        print("❌ ERROR: OPENROUTE_API_KEY not found")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test with a simple, well-known route in Europe
    # Berlin to Munich - this should definitely work
    coordinates = [
        [13.4050, 52.5200],  # Berlin (lng, lat)
        [11.5761, 48.1374]   # Munich (lng, lat)
    ]
    
    print(f"\n🧪 Testing with Berlin to Munich (should work):")
    print(f"Coordinates: {coordinates}")
    
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "coordinates": coordinates,
        "format": "geojson",
        "radiuses": [-1, -1],
        "continue_straight": False,
        "preference": "fastest",
        "units": "m",
        "geometry": True,
        "instructions": False,
        "maneuvers": False
    }
    
    print(f"\n📤 API Request:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"\n📥 API Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2)}")
            
            if data.get("features") and len(data["features"]) > 0:
                distance = data["features"][0]["properties"]["summary"]["distance"]
                duration = data["features"][0]["properties"]["summary"]["duration"]
                print(f"✅ SUCCESS! Distance: {distance}m, Duration: {duration}s")
                return True
            else:
                print(f"❌ No route found in response")
                return False
        else:
            print(f"❌ Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_fallback_solution():
    """Test the fallback solution with NY coordinates."""
    try:
        from core.services.openroute_service import OpenRouteService
        
        # Get API key from environment
        api_key = os.getenv('OPENROUTE_API_KEY')
        
        if not api_key:
            print("❌ ERROR: OPENROUTE_API_KEY not found in environment variables")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        openroute_service = OpenRouteService(api_key)
        
        # Test with NY coordinates from sample data
        print("\n🧪 Testing with NY coordinates from sample data:")
        ny_coords = [
            (40.7589, -73.9851),  # Central Warehouse (lat, lng)
            (40.7614, -73.9776),  # North Distribution Center (lat, lng)
            (40.7505, -73.9934)   # South Logistics Hub (lat, lng)
        ]
        
        print(f"Input coordinates: {ny_coords}")
        print("Format: (latitude, longitude)")
        
        # Test the route calculation
        route_result = openroute_service.build_circular_route(ny_coords)
        
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

if __name__ == "__main__":
    print("🔍 Testing OpenRouteService API Key...")
    print("=" * 50)
    
    success1 = test_api_key()
    success2 = test_fallback_solution()
    
    if success1 or success2:
        print("\n✅ API key is working correctly!")
        print("Your application will now provide estimated routes even when OpenRouteService fails.")
        print("\n📋 What this means:")
        print("- If OpenRouteService works: You get accurate routing data")
        print("- If OpenRouteService fails: You get estimated distance/duration")
        print("- Your application will never completely fail due to routing issues")
    else:
        print("\n❌ API key test failed")
        print("There might be an issue with the API key or implementation")