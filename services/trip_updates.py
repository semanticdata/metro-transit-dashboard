import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
from tabulate import tabulate
from flask import Flask, render_template
import json

app = Flask(__name__)

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
    return datetime.fromtimestamp(timestamp).strftime('%I:%M %p')

def get_trip_updates():
    """Get trip updates in a format suitable for the template"""
    feed = fetch_trip_updates()
    if not feed:
        return []
    
    updates = []
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip = entity.trip_update.trip
            
            stop_time = None
            if entity.trip_update.stop_time_update:
                stop_time = entity.trip_update.stop_time_update[0]
            
            update = {
                'trip_id': trip.trip_id,
                'route_id': trip.route_id if trip.HasField('route_id') else 'N/A',
                'schedule': trip.schedule_relationship if trip.HasField('schedule_relationship') else 'SCHEDULED',
                'stop_id': stop_time.stop_id if stop_time else 'N/A',
                'arrival': format_timestamp(stop_time.arrival.time) if stop_time and stop_time.HasField('arrival') else 'N/A',
                'departure': format_timestamp(stop_time.departure.time) if stop_time and stop_time.HasField('departure') else 'N/A'
            }
            updates.append(update)
    
    return updates

@app.route('/')
def dashboard():
    updates = get_trip_updates()
    return render_template('trip-updates.html', updates=updates)

if __name__ == "__main__":
    app.run(debug=True)
