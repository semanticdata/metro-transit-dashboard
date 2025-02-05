from flask import Flask, render_template
from services.trip_updates import get_trip_updates
from services.service_alerts import fetch_service_alerts
from services.vehicle_position import fetch_vehicle_positions
from services.routes import MetroTransitAPI

app = Flask(__name__)


@app.route('/')
def index():
    """Main dashboard page combining all transit information"""
    return render_template('index.html')


@app.route('/trip-updates')
def trip_updates():
    """Trip updates page"""
    updates = get_trip_updates()
    return render_template('trip-updates.html', updates=updates)


@app.route('/service-alerts')
def service_alerts():
    """Service alerts page"""
    alerts = fetch_service_alerts()
    return render_template('service-alerts.html', alerts=alerts)


@app.route('/vehicle-positions')
def vehicle_positions():
    """Vehicle positions page"""
    vehicles = fetch_vehicle_positions()
    return render_template('vehicle-positions.html', vehicles=vehicles)


@app.route('/map')
def map_view():
    """Interactive map showing current vehicle positions"""
    vehicles = fetch_vehicle_positions()
    return render_template('map.html', vehicles=vehicles)


@app.route('/routes')
def routes():
    """Routes information page"""
    api = MetroTransitAPI()
    routes_data = api.get_routes()
    return render_template('routes.html', routes=routes_data)


if __name__ == "__main__":
    app.run(debug=True)
