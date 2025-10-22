#!/usr/bin/env python3
"""
Test script to verify Google Maps API key configuration.
Run this to check if your API key is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_google_maps_api():
    """Test Google Maps API key configuration."""
    try:
        from truck_management.core.services.openroute_service import OpenRouteService
        
        # Get API key from environment
        api_key = os.getenv('OPENROUTE_API_KEY')
        
        if not api_key:
            print("❌ ERROR: OPENROUTE_API_KEY not found in environment variables")
            print("   Make sure you have a .env file with OPENROUTE_API_KEY=your_key")
            return False
        
        if api_key == 'your_actual_openroute_api_key_here':
            print("❌ ERROR: Please replace 'your_actual_openroute_api_key_here' with your real API key")
            return False
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Test geocoding
        print("🔍 Testing geocoding...")
        google_maps = OpenRouteService(api_key)
        
        # Test with a simple address
        result = google_maps.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
        
        if 'error_message' in result:
            print(f"❌ Geocoding failed: {result['error_message']}")
            return False
        
        if result.get('status') == 'OK':
            print("✅ Geocoding test passed!")
        else:
            print(f"❌ Geocoding failed with status: {result.get('status')}")
            return False
        
        # Test directions
        print("🗺️ Testing directions...")
        test_points = [
            (37.4224764, -122.0842499),  # Google HQ
            (37.7749, -122.4194),       # San Francisco
        ]
        
        route_result = google_maps.build_circular_route(test_points)
        
        if 'error' in route_result:
            print(f"❌ Directions failed: {route_result['error']}")
            return False
        
        print("✅ Directions test passed!")
        print("🎉 All tests passed! Your Google Maps API key is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Maps API Configuration...")
    print("=" * 50)
    
    success = test_google_maps_api()
    
    if not success:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Make sure you have a .env file in the project root")
        print("2. Check that GOOGLE_MAPS_API_KEY is set correctly")
        print("3. Verify your API key has Directions API and Geocoding API enabled")
        print("4. Check if your API key has proper restrictions set")
        print("5. Make sure billing is enabled for your Google Cloud project")
    else:
        print("\n✅ Your Google Maps integration is ready to use!")
