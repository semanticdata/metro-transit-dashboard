import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
from datetime import datetime


def fetch_service_alerts():
    """Fetch service alerts from Metro Transit GTFS realtime feed"""
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
                "header": alert.header_text.translation[0].text
                if alert.header_text.translation
                else "No header",
                "description": alert.description_text.translation[0].text
                if alert.description_text.translation
                else "No description",
                "effect": str(alert.effect) if alert.effect else "UNKNOWN_EFFECT",
                "cause": str(alert.cause) if alert.cause else "UNKNOWN_CAUSE",
                "affected_routes": [
                    entity.route_id
                    for entity in alert.informed_entity
                    if entity.route_id
                ],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            alerts_data.append(alert_data)

        return alerts_data

    except requests.exceptions.RequestException as e:
        return [{"error": f"Error fetching alerts: {e}"}]
    except Exception as e:
        return [{"error": f"Error processing alerts: {e}"}]


def fetch_vehicle_positions():
    """Fetch and parse vehicle position data from Metro Transit"""
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

            # Convert timestamp to readable format
            timestamp = datetime.fromtimestamp(vehicle.timestamp)

            # Create vehicle dictionary
            vehicle_data = {
                "vehicle_id": vehicle.vehicle.id,
                "trip_id": vehicle.trip.trip_id,
                "route_id": vehicle.trip.route_id,
                "latitude": vehicle.position.latitude,
                "longitude": vehicle.position.longitude,
                "speed": vehicle.position.speed
                if vehicle.position.HasField("speed")
                else "N/A",
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            vehicles.append(vehicle_data)

        return vehicles

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except DecodeError as e:
        print(f"Error decoding protobuf: {e}")
        return []


def fetch_trip_updates():
    """Fetch GTFS realtime trip updates from Metro Transit"""
    url = "https://svc.metrotransit.org/mtgtfs/tripupdates.pb"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            return None

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        print(f"Error: {e}")
        return None


def format_timestamp(timestamp):
    """Convert POSIX timestamp to readable datetime"""
    return datetime.fromtimestamp(timestamp).strftime("%I:%M %p")


def get_trip_updates():
    """Get trip updates in a format suitable for the template"""
    feed = fetch_trip_updates()
    if not feed:
        return []

    updates = []
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            trip = entity.trip_update.trip

            stop_time = None
            if entity.trip_update.stop_time_update:
                stop_time = entity.trip_update.stop_time_update[0]

            update = {
                "trip_id": trip.trip_id,
                "route_id": trip.route_id if trip.HasField("route_id") else "N/A",
                "schedule": trip.schedule_relationship
                if trip.HasField("schedule_relationship")
                else "SCHEDULED",
                "stop_id": stop_time.stop_id if stop_time else "N/A",
                "arrival": format_timestamp(stop_time.arrival.time)
                if stop_time and stop_time.HasField("arrival")
                else "N/A",
                "departure": format_timestamp(stop_time.departure.time)
                if stop_time and stop_time.HasField("departure")
                else "N/A",
            }
            updates.append(update)

    return updates
