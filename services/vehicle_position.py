import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.message import DecodeError
from datetime import datetime
from flask import Flask, render_template
import json

app = Flask(__name__)

def fetch_vehicle_positions():
    """Fetch and parse vehicle position data from Metro Transit"""
    url = 'https://svc.metrotransit.org/mtgtfs/vehiclepositions.pb'
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
                'vehicle_id': vehicle.vehicle.id,
                'trip_id': vehicle.trip.trip_id,
                'route_id': vehicle.trip.route_id,
                'latitude': vehicle.position.latitude,
                'longitude': vehicle.position.longitude,
                'speed': vehicle.position.speed if vehicle.position.HasField('speed') else 'N/A',
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            vehicles.append(vehicle_data)
            
        return vehicles
            
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    except DecodeError as e:
        print(f"Error decoding protobuf: {e}")
        return []

@app.route('/')
def dashboard():
    vehicles = fetch_vehicle_positions()
    return render_template('vehicle-positions.html', vehicles=vehicles)

if __name__ == "__main__":
    app.run(debug=True)
