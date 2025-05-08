import sys
import json
from routes import MetroTransitAPI

def get_all_stops_with_location(route_id):
    api = MetroTransitAPI()
    stops_info = []
    directions = api.get_directions(route_id)
    for direction in directions:
        direction_id = direction.get("direction_id")
        stops = api.get_stops(route_id, direction_id)
        for stop in stops:
            place_code = stop.get("place_code")
            stop_details = api.get_stop_details(route_id, direction_id, place_code)
            if stop_details:
                stop_info = {
                    "route_id": route_id,
                    "direction_id": direction_id,
                    "place_code": place_code,
                    "description": stop_details.get("description", place_code),
                    "latitude": stop_details.get("latitude"),
                    "longitude": stop_details.get("longitude"),
                    "stop_id": stop_details.get("stop_id")
                }
                stops_info.append(stop_info)
    return stops_info

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_route_stops.py <route_id> [output_file.json]")
        sys.exit(1)
    route_id = sys.argv[1]
    stops = get_all_stops_with_location(route_id)
    output = json.dumps(stops, indent=2)
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Wrote stops to {output_file}")
    else:
        print(output)
