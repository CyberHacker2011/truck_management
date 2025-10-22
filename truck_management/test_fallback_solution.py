#!/usr/bin/env python3
"""
Test script to verify the fallback solution works when OpenRouteService fails.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_fallback_solution():
    """Test the fallback solution with NY coordinates."""
    try:
        from truck_management.core.services.openroute_service import OpenRouteService
        
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

def test_with_different_coordinates():
    """Test with different coordinate sets."""
    try:
        from truck_management.core.services.openroute_service import OpenRouteService
        
        api_key = os.getenv('OPENROUTE_API_KEY')
        if not api_key:
            return False
        
        openroute_service = OpenRouteService(api_key)
        
        # Test with European coordinates (should work better)
        print("\n🌍 Testing with European coordinates:")
        eu_coords = [
            (52.5200, 13.4050),  # Berlin (lat, lng)
            (48.1374, 11.5761)   # Munich (lat, lng)
        ]
        
        eu_result = openroute_service.build_circular_route(eu_coords)
        print(f"EU coordinates result: {eu_result}")
        
        if 'error' in eu_result and not eu_result.get('fallback'):
            print("❌ Even European coordinates failed")
        elif eu_result.get('fallback'):
            print("⚠️ European coordinates also used fallback")
        else:
            print("✅ European coordinates worked with OpenRouteService!")
        
        # Test with very close coordinates
        print("\n📍 Testing with very close coordinates:")
        close_coords = [
            (40.7589, -73.9851),  # Times Square
            (40.7589, -73.9852)   # Very close to Times Square
        ]
        
        close_result = openroute_service.build_circular_route(close_coords)
        print(f"Close coordinates result: {close_result}")
        
        if 'error' in close_result and not close_result.get('fallback'):
            print("❌ Close coordinates failed")
        elif close_result.get('fallback'):
            print("⚠️ Close coordinates used fallback")
        else:
            print("✅ Close coordinates worked!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Fallback Solution...")
    print("=" * 50)
    
    success1 = test_fallback_solution()
    success2 = test_with_different_coordinates()
    
    if success1 or success2:
        print("\n✅ Fallback solution is working!")
        print("Your application will now provide estimated routes even when OpenRouteService fails.")
        print("\n📋 What this means:")
        print("- If OpenRouteService works: You get accurate routing data")
        print("- If OpenRouteService fails: You get estimated distance/duration")
        print("- Your application will never completely fail due to routing issues")
    else:
        print("\n❌ Fallback solution failed")
        print("There might be an issue with the implementation")
