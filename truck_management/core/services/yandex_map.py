import os
from typing import List, Tuple, Dict, Any


class YandexMapService:
    """
    Thin wrapper around Yandex Maps APIs (Geocoder + Routing).
    Provides geocoding and circular route generation across multiple points.
    """

    GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"
    ROUTING_URL = "https://api.routing.yandex.net/v2/route"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv('YANDEX_API_KEY')

    def geocode(self, address: str) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('YANDEX_API_KEY is not configured')
        try:
            import requests
        except ImportError as e:
            raise RuntimeError('The requests package is required for Yandex API calls') from e
        params = {
            'apikey': self.api_key,
            'format': 'json',
            'geocode': address,
            'lang': 'en_US',
        }
        response = requests.get(self.GEOCODER_URL, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def build_circular_route(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """
        Build a circular route that starts at the first point, visits all points,
        and returns to the start. Uses Yandex Routing API v2.
        """
        if len(points) < 1:
            return {}
        if not self.api_key:
            raise RuntimeError('YANDEX_API_KEY is not configured')
        try:
            import requests
        except ImportError as e:
            raise RuntimeError('The requests package is required for Yandex API calls') from e

        # Prepare waypoints: start -> intermediate -> back to start
        start = points[0]
        waypoints = [start] + points[1:] + [start]

        # Format for Yandex API: lon,lat in each point
        points_param = [{
            "point": {
                "lon": float(lon),
                "lat": float(lat)
            }
        } for lat, lon in waypoints]

        payload: Dict[str, Any] = {
            "apikey": self.api_key,
            "waypoints": points_param,
            "mode": {
                "type": "driving"
            },
            "routingMode": "fastest"
        }

        # Yandex routing expects POST with JSON body and apikey in query or header; we pass as query
        params = {"apikey": self.api_key}
        response = requests.post(self.ROUTING_URL, params=params, json={
            "waypoints": points_param,
            "mode": {"type": "driving"},
            "routingMode": "fastest"
        }, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data


