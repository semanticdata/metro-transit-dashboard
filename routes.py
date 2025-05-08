import requests
from typing import Dict, List


class MetroTransitAPI:
    def __init__(self):
        self.base_url = "https://svc.metrotransit.org/nextrip"

    def get_routes(self) -> List[Dict]:
        """Get all available routes"""
        response = requests.get(
            f"{self.base_url}/routes", headers={"Accept": "application/json"}
        )
        return response.json()

    def get_directions(self, route_id: str) -> List[Dict]:
        """Get directions for a specific route"""
        response = requests.get(
            f"{self.base_url}/directions/{route_id}",
            headers={"Accept": "application/json"},
        )
        return response.json()

    def get_stops(self, route_id: str, direction_id: int) -> List[Dict]:
        """Get stops for a route and direction"""
        response = requests.get(
            f"{self.base_url}/stops/{route_id}/{direction_id}",
            headers={"Accept": "application/json"},
        )
        return response.json()

    def get_stop_details(
        self, route_id: str, direction_id: int, place_code: str
    ) -> Dict:
        """Get details for a specific stop by its route_id, direction_id, and place_code"""
        response = requests.get(
            f"{self.base_url}/{route_id}/{direction_id}/{place_code}",
            headers={"Accept": "application/json"},
        )
        data = response.json()
        # According to the schema, the stop details are in a 'stops' array
        if (
            isinstance(data, dict)
            and "stops" in data
            and isinstance(data["stops"], list)
            and data["stops"]
        ):
            return data["stops"][
                0
            ]  # Return the first stop object from the 'stops' list
        return None  # Return None if 'stops' key is missing, not a list, or empty
