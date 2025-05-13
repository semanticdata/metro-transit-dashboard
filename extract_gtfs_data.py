import json
from datetime import datetime
import os
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
import requests

def extract_service_alerts():
    """Extract service alerts from GTFS feed and save to JSON"""
    url = "https://svc.metrotransit.org/mtgtfs/alerts.pb"
    alerts_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        for entity in feed.entity:
            alert = entity.alert
            alert_data = {
                "id": entity.id,
                "header": alert.header_text.translation[0].text if alert.header_text.translation else "No header",
                "description": alert.description_text.translation[0].text if alert.description_text.translation else "No description",
                "effect": str(alert.effect) if alert.effect else "UNKNOWN_EFFECT",
                "cause": str(alert.cause) if alert.cause else "UNKNOWN_CAUSE",
                "affected_routes": [entity.route_id for entity in alert.informed_entity if entity.route_id],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            alerts_data.append(alert_data)

        # Create output directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate filename with timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/service_alerts_{current_time}.json"
        
        # Save to JSON file
        with open(filename, 'w') as f:
            json.dump(alerts_data, f, indent=2)
            
        print(f"Successfully saved {len(alerts_data)} service alerts to {filename}")
        return alerts_data

    except requests.RequestException as e:
        print(f"Error fetching alerts data: {e}")
        return []
    except DecodeError as e:
        print(f"Error decoding alerts protobuf: {e}")
        return []

def extract_trip_updates():
    """Extract trip updates from GTFS feed and save to JSON"""
    url = "https://svc.metrotransit.org/mtgtfs/tripupdates.pb"
    updates = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip = entity.trip_update.trip
                stop_time = None
                if entity.trip_update.stop_time_update:
                    stop_time = entity.trip_update.stop_time_update[0]

                update = {
                    "trip_id": trip.trip_id,
                    "route_id": trip.route_id if trip.HasField("route_id") else "N/A",
                    "schedule": trip.schedule_relationship if trip.HasField("schedule_relationship") else "SCHEDULED",
                    "stop_id": stop_time.stop_id if stop_time else "N/A",
                    "arrival": datetime.fromtimestamp(stop_time.arrival.time).strftime("%I:%M %p") if stop_time and stop_time.HasField("arrival") else "N/A",
                    "departure": datetime.fromtimestamp(stop_time.departure.time).strftime("%I:%M %p") if stop_time and stop_time.HasField("departure") else "N/A",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                updates.append(update)

        # Create output directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate filename with timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/trip_updates_{current_time}.json"
        
        # Save to JSON file
        with open(filename, 'w') as f:
            json.dump(updates, f, indent=2)
            
        print(f"Successfully saved {len(updates)} trip updates to {filename}")
        return updates

    except requests.RequestException as e:
        print(f"Error fetching trip updates data: {e}")
        return []
    except DecodeError as e:
        print(f"Error decoding trip updates protobuf: {e}")
        return []

def extract_vehicle_data():
    """Extract all available fields from GTFS vehicle position feed and save to JSON"""
    url = "https://svc.metrotransit.org/mtgtfs/vehiclepositions.pb"
    vehicles = []

    try:
        # Fetch the protobuf data
        response = requests.get(url)
        response.raise_for_status()

        # Parse the protobuf message
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        # Process each vehicle position
        for entity in feed.entity:
            vehicle = entity.vehicle
            timestamp = datetime.fromtimestamp(vehicle.timestamp)

            # Create comprehensive vehicle dictionary with all available fields
            vehicle_data = {
                # Basic vehicle information
                "vehicle_id": vehicle.vehicle.id,
                "label": vehicle.vehicle.label if vehicle.vehicle.HasField("label") else None,
                "license_plate": vehicle.vehicle.license_plate if vehicle.vehicle.HasField("license_plate") else None,
                
                # Trip information
                "trip_id": vehicle.trip.trip_id,
                "route_id": vehicle.trip.route_id,
                "direction_id": vehicle.trip.direction_id if vehicle.trip.HasField("direction_id") else None,
                "start_time": vehicle.trip.start_time if vehicle.trip.HasField("start_time") else None,
                "start_date": vehicle.trip.start_date if vehicle.trip.HasField("start_date") else None,
                "schedule_relationship": vehicle.trip.schedule_relationship if vehicle.trip.HasField("schedule_relationship") else None,
                
                # Position information
                "latitude": vehicle.position.latitude,
                "longitude": vehicle.position.longitude,
                "bearing": vehicle.position.bearing if vehicle.position.HasField("bearing") else None,
                "odometer": vehicle.position.odometer if vehicle.position.HasField("odometer") else None,
                "speed": vehicle.position.speed if vehicle.position.HasField("speed") else None,
                
                # Current stop information
                "current_stop_sequence": vehicle.current_stop_sequence if vehicle.HasField("current_stop_sequence") else None,
                "stop_id": vehicle.stop_id if vehicle.HasField("stop_id") else None,
                "current_status": vehicle.current_status if vehicle.HasField("current_status") else None,
                
                # Additional information
                "congestion_level": vehicle.congestion_level if vehicle.HasField("congestion_level") else None,
                "occupancy_status": vehicle.occupancy_status if vehicle.HasField("occupancy_status") else None,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            vehicles.append(vehicle_data)

        # Create output directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Generate filename with timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/vehicle_positions_{current_time}.json"
        
        # Save to JSON file
        with open(filename, 'w') as f:
            json.dump(vehicles, f, indent=2)
            
        print(f"Successfully saved {len(vehicles)} vehicle positions to {filename}")
        return vehicles

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except DecodeError as e:
        print(f"Error decoding protobuf: {e}")
        return []

if __name__ == "__main__":
    # Extract data from all three endpoints
    vehicle_data = extract_vehicle_data()
    service_alerts = extract_service_alerts()
    trip_updates = extract_trip_updates()
    
    print("\nData extraction complete!")
    print(f"Extracted {len(vehicle_data)} vehicle positions")
    print(f"Extracted {len(service_alerts)} service alerts")
    print(f"Extracted {len(trip_updates)} trip updates")