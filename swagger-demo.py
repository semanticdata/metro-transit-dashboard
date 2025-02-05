import requests
import json
from typing import Dict, List

class MetroTransitAPI:
    def __init__(self):
        self.base_url = "https://svc.metrotransit.org/nextripv2"

    def get_routes(self) -> List[Dict]:
        """Get all available routes"""
        response = requests.get(f"{self.base_url}/routes")
        return response.json()

    def get_directions(self, route_id: str) -> List[Dict]:
        """Get directions for a specific route"""
        response = requests.get(f"{self.base_url}/directions/{route_id}")
        return response.json()

    def get_stops(self, route_id: str, direction_id: int) -> List[Dict]:
        """Get stops for a route and direction"""
        response = requests.get(f"{self.base_url}/stops/{route_id}/{direction_id}")
        return response.json()

def main():
    api = MetroTransitAPI()
    
    # Get and display all routes
    print("Available Routes:")
    print("-" * 50)
    routes = api.get_routes()
    for route in routes:
        print(f"Route {route['route_id']}: {route['route_label']}")
    
    # Demo with a specific route (using the first route as an example)
    if routes:
        selected_route = routes[0]['route_id']
        print(f"\nGetting directions for route {selected_route}")
        print("-" * 50)
        
        # Get directions for the selected route
        directions = api.get_directions(selected_route)
        for direction in directions:
            print(f"Direction {direction['direction_id']}: {direction['direction_name']}")
            
            # Get stops for this route and direction
            stops = api.get_stops(selected_route, direction['direction_id'])
            print("\nStops:")
            for stop in stops:
                print(f"- {stop['description']} (Stop #: {stop['place_code']})")
            print()

if __name__ == "__main__":
    main()
