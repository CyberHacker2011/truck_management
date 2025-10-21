"""
GOOGLE MAPS SERVICE - COMMENTED OUT FOR REFERENCE

This file contains the original Google Maps integration code commented out for reference.
The active OpenRouteService implementation is now in openroute_service.py
"""

# import os
# import requests
# from typing import List, Tuple, Dict, Any


# class GoogleMapService:
#     """
#     Wrapper around Google Maps Directions and Geocoding APIs.
#     Used for route generation and address-coordinate conversions.
#     """

#     GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
#     DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

#     def __init__(self, api_key: str | None = None):
#         self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
#         if not self.api_key:
#             raise RuntimeError("GOOGLE_MAPS_API_KEY is not configured")

#     def geocode(self, address: str) -> Dict[str, Any]:
#         """Convert an address string to coordinates."""
#         params = {"address": address, "key": self.api_key}
#         response = requests.get(self.GEOCODE_URL, params=params, timeout=20)
#         response.raise_for_status()
#         return response.json()

#     def build_circular_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
#         """
#         Build a circular route: start → waypoints → return to start.
#         Returns route polyline + distance + duration from Google Directions API.
#         """
#         if len(points) < 2:
#             return {"error": "not_enough_points"}

#         origin = f"{points[0][0]},{points[0][1]}"
#         destination = origin
#         waypoints = "|".join(f"{lat},{lon}" for lat, lon in points[1:])

#         params = {
#             "origin": origin,
#             "destination": destination,
#             "waypoints": waypoints,
#             "key": self.api_key,
#             "mode": "driving",
#             "optimizeWaypoints": "true",
#         }

#         try:
#             response = requests.get(self.DIRECTIONS_URL, params=params, timeout=30)
#             response.raise_for_status()
#             data = response.json()
#             if data.get("status") != "OK":
#                 return {"error": "routing_failed", "message": data.get("status")}
#             return {
#                 "distance": sum(leg["distance"]["value"] for leg in data["routes"][0]["legs"]),
#                 "duration": sum(leg["duration"]["value"] for leg in data["routes"][0]["legs"]),
#                 "polyline": data["routes"][0]["overview_polyline"]["points"],
#                 "raw": data,
#             }
#         except Exception as exc:
#             return {
#                 "error": "routing_failed",
#                 "message": str(exc),
#             }

