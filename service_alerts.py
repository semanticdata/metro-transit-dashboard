import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime
import json

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
                'id': entity.id,
                'header': alert.header_text.translation[0].text if alert.header_text.translation else "No header",
                'description': alert.description_text.translation[0].text if alert.description_text.translation else "No description",
                'effect': str(alert.effect) if alert.effect else "UNKNOWN_EFFECT",
                'cause': str(alert.cause) if alert.cause else "UNKNOWN_CAUSE",
                'affected_routes': [entity.route_id for entity in alert.informed_entity if entity.route_id],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            alerts_data.append(alert_data)
            
        return alerts_data

    except requests.exceptions.RequestException as e:
        return [{'error': f"Error fetching alerts: {e}"}]
    except Exception as e:
        return [{'error': f"Error processing alerts: {e}"}]
