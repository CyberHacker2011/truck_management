"""
OpenRouteService API Integration

Production-ready Django service for handling routing using OpenRouteService API.
This replaces the previous Google Maps integration while maintaining clean,
minimal, and well-structured code for Django integration.
"""

import os
import requests
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings


class OpenRouteService:
    """
    OpenRouteService API client for routing functionality.
    
    Provides clean, production-ready methods for getting driving directions
    between coordinates using the OpenRouteService API.
    """
    
    BASE_URL = "https://api.openrouteservice.org/v2/directions"
    ROUTE_TYPE = "driving-car"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouteService client.
        
        Args:
            api_key: OpenRouteService API key. If not provided, will attempt
                    to get from environment variable OPENROUTE_API_KEY
        """
        self.api_key = api_key or os.getenv("OPENROUTE_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTE_API_KEY environment variable is required")
    
    def get_route(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> Dict[str, Any]:
        """
        Get driving route between two coordinates using OpenRouteService API.
        
        Args:
            start_lat: Starting latitude
            start_lng: Starting longitude  
            end_lat: Ending latitude
            end_lng: Ending longitude
            
        Returns:
            Dict containing the full parsed JSON result from OpenRouteService API
            or error information if the request fails
            
        Example:
            >>> service = OpenRouteService()
            >>> result = service.get_route(49.41461, 8.681495, 49.420318, 8.687872)
            >>> if 'error' not in result:
            ...     print(f"Distance: {result['features'][0]['properties']['summary']['distance']}m")
        """
        url = f"{self.BASE_URL}/{self.ROUTE_TYPE}"
        
        # Prepare coordinates in [longitude, latitude] format as required by ORS
        coordinates = [[start_lng, start_lat], [end_lng, end_lat]]
        
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "coordinates": coordinates,
            "format": "geojson",
            "radiuses": [-1, -1],  # -1 means no radius restriction
            "continue_straight": False,
            "preference": "fastest",
            "units": "m",
            "geometry": True,
            "instructions": False,
            "maneuvers": False
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API-level errors
            if "error" in data:
                return {
                    "error": "api_error",
                    "message": data.get("error", {}).get("message", "Unknown API error"),
                    "details": data.get("error", {})
                }
            
            # Check if route was found
            if not data.get("features") or len(data["features"]) == 0:
                return {
                    "error": "no_route_found",
                    "message": "No route could be calculated between the given coordinates"
                }
            
            return data
            
        except requests.exceptions.Timeout:
            return {
                "error": "timeout_error",
                "message": "Request to OpenRouteService API timed out"
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": "connection_error", 
                "message": "Failed to connect to OpenRouteService API"
            }
        except requests.exceptions.HTTPError as e:
            return {
                "error": "http_error",
                "message": f"HTTP error {e.response.status_code}: {str(e)}",
                "status_code": e.response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": "request_error",
                "message": f"Request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "error": "unexpected_error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def build_circular_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Build a circular route: start → waypoints → return to start.
        Compatible method for existing code that expects this interface.
        
        Args:
            points: List of (latitude, longitude) tuples
            
        Returns:
            Dict containing distance, duration, geometry, and polyline data
        """
        if len(points) < 2:
            return {"error": "not_enough_points"}
        
        # Get route from first point to last point
        start_lat, start_lng = points[0]
        end_lat, end_lng = points[-1]
        
        route_data = self.get_route(start_lat, start_lng, end_lat, end_lng)
        
        if "error" in route_data:
            return route_data
        
        try:
            feature = route_data["features"][0]
            properties = feature["properties"]
            summary = properties.get("summary", {})
            
            return {
                "distance": summary.get("distance", 0),  # meters
                "duration": summary.get("duration", 0),  # seconds
                "geometry": feature.get("geometry", {}),
                "polyline": feature.get("geometry", {}),  # For compatibility
                "raw": route_data
            }
        except (KeyError, IndexError) as e:
            return {
                "error": "parsing_error",
                "message": f"Failed to parse route data: {str(e)}"
            }
    
    def get_route_summary(self, start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> Dict[str, Any]:
        """
        Get simplified route summary with distance, duration, and basic info.
        
        Args:
            start_lat: Starting latitude
            start_lng: Starting longitude
            end_lat: Ending latitude  
            end_lng: Ending longitude
            
        Returns:
            Dict containing distance (meters), duration (seconds), and geometry
        """
        route_data = self.get_route(start_lat, start_lng, end_lat, end_lng)
        
        if "error" in route_data:
            return route_data
        
        try:
            feature = route_data["features"][0]
            properties = feature["properties"]
            summary = properties.get("summary", {})
            
            return {
                "distance": summary.get("distance", 0),  # meters
                "duration": summary.get("duration", 0),  # seconds
                "geometry": feature.get("geometry", {}),
                "coordinates": coordinates,
                "raw_data": route_data
            }
        except (KeyError, IndexError) as e:
            return {
                "error": "parsing_error",
                "message": f"Failed to parse route data: {str(e)}"
            }


# =============================================================================
# LEGACY GOOGLE MAPS INTEGRATION (COMMENTED FOR REFERENCE)
# =============================================================================

"""
# Previous Google Maps integration structure for reference:

import os
import requests
from typing import List, Tuple, Dict, Any

class GoogleMapService:
    GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_MAPS_API_KEY is not configured")

    def geocode(self, address: str) -> Dict[str, Any]:
        params = {"address": address, "key": self.api_key}
        response = requests.get(self.GEOCODE_URL, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def build_circular_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        if len(points) < 2:
            return {"error": "not_enough_points"}

        origin = f"{points[0][0]},{points[0][1]}"
        destination = origin
        waypoints = "|".join(f"{lat},{lon}" for lat, lon in points[1:])

        params = {
            "origin": origin,
            "destination": destination,
            "waypoints": waypoints,
            "key": self.api_key,
            "mode": "driving",
            "optimizeWaypoints": "true",
        }

        try:
            response = requests.get(self.DIRECTIONS_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "OK":
                return {"error": "routing_failed", "message": data.get("status")}
            return {
                "distance": sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"]),
                "duration": sum(leg["duration"]["value"] for leg in data["routes"][0]["legs"]),
                "polyline": data["routes"][0]["overview_polyline"]["points"],
                "raw": data,
            }
        except Exception as exc:
            return {
                "error": "routing_failed",
                "message": str(exc),
            }

# Usage example for Google Maps:
# service = GoogleMapService()
# result = service.build_circular_route([(49.41461, 8.681495), (49.420318, 8.687872)])
"""
