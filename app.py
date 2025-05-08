import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Import data fetching functions from other modules
# These will be used in callbacks later
from gtfs_trip_updates import get_trip_updates
from gtfs_service_alerts import fetch_service_alerts
from gtfs_vehicle_position import fetch_vehicle_positions
from routes import MetroTransitAPI

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose server for Gunicorn or other WSGI servers

# Define the layout of the application
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.H1("Metro Transit Dashboard"),
        html.Nav(
            [
                dcc.Link("Home", href="/"),
                html.Br(),
                dcc.Link("Trip Updates", href="/trip-updates"),
                html.Br(),
                dcc.Link("Service Alerts", href="/service-alerts"),
                html.Br(),
                dcc.Link("Vehicle Positions", href="/vehicle-positions"),
                html.Br(),
                dcc.Link("Map", href="/map"),
                html.Br(),
                dcc.Link("Routes", href="/routes"),
                html.Br(),
                dcc.Link("Blue Line Map", href="/blue-line-map"),
            ]
        ),
        html.Hr(),
        html.Div(id="page-content"),
    ]
)


# Callback to update page content based on URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/trip-updates":
        updates = get_trip_updates()
        return html.Div(
            [
                html.H3("Trip Updates"),
                html.Ul(
                    [
                        html.Li(
                            f"{update['trip_id']} - Route: {update['route_id']} - Arrival: {update.get('arrival', update.get('departure', 'N/A'))}"
                        )
                        for update in updates
                    ]
                ),
            ]
        )
    elif pathname == "/service-alerts":
        alerts = fetch_service_alerts()
        # Support both old (header/description) and new (alert_text/stop_closed) alert formats
        return html.Div(
            [
                html.H3("Service Alerts"),
                html.Ul(
                    [
                        html.Li(
                            alert.get("alert_text")
                            if "alert_text" in alert
                            else f"{alert.get('header', 'N/A')}: {alert.get('description', 'N/A')}"
                        )
                        for alert in alerts
                    ]
                ),
            ]
        )
    elif pathname == "/vehicle-positions":
        vehicles = fetch_vehicle_positions()
        return html.Div(
            [
                html.H3("Vehicle Positions"),
                html.Ul(
                    [
                        html.Li(
                            f"Vehicle {vehicle.get('vehicle_id', 'N/A')} on route {vehicle.get('route_id', 'N/A')} at ({vehicle.get('latitude', 'N/A')}, {vehicle.get('longitude', 'N/A')}) at {vehicle.get('timestamp', 'N/A')}"
                        )
                        for vehicle in vehicles
                    ]
                ),
            ]
        )
    elif pathname == "/map":
        vehicles = fetch_vehicle_positions()
        if vehicles and (
            isinstance(vehicles, list) and (not vehicles or "error" not in vehicles[0])
        ):
            import plotly.express as px

            fig = px.scatter_map(
                vehicles,
                lat="latitude",
                lon="longitude",
                hover_name="vehicle_id",
                hover_data=["route_id", "timestamp"],
                color_discrete_sequence=["blue"],
                zoom=10,
                height=600,
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return html.Div([html.H3("Map View"), dcc.Graph(figure=fig)])
        else:
            return html.Div(
                [
                    html.H3("Map View"),
                    html.P("Could not load vehicle data for the map."),
                ]
            )
    elif pathname == "/routes":
        api = MetroTransitAPI()
        routes_data = api.get_routes()
        return html.Div(
            [
                html.H3("Routes"),
                html.Ul(
                    [
                        html.Li(
                            f"{route.get('route_label', 'N/A')} (ID: {route.get('route_id', 'N/A')})"
                        )
                        for route in routes_data
                    ]
                ),
            ]
        )
    elif pathname == "/blue-line-map":
        api = MetroTransitAPI()
        blue_line_route_id = "901"  # Blue Line route_id is 901
        # Get all directions for Blue Line
        directions = api.get_directions(blue_line_route_id)
        blue_line_stops = []
        for direction in directions:
            direction_id = direction.get("direction_id")
            stops = api.get_stops(blue_line_route_id, direction_id)
            for stop in stops:
                place_code = stop.get("place_code")
                stop_details = api.get_stop_details(
                    blue_line_route_id, direction_id, place_code
                )
                if (
                    stop_details
                    and "latitude" in stop_details
                    and "longitude" in stop_details
                ):
                    blue_line_stops.append(
                        {
                            "lat": stop_details["latitude"],
                            "lon": stop_details["longitude"],
                            "description": stop_details.get("description", place_code),
                        }
                    )
        # Remove duplicates and sort by lat/lon for a cleaner line (optional, can be improved)
        seen = set()
        unique_stops = []
        for stop in blue_line_stops:
            key = (stop["lat"], stop["lon"])
            if key not in seen:
                unique_stops.append(stop)
                seen.add(key)
        # Get Blue Line vehicles
        vehicles = fetch_vehicle_positions()
        blue_line_vehicles = [
            v for v in vehicles if v.get("route_id") == blue_line_route_id
        ]
        import plotly.express as px
        import plotly.graph_objects as go

        fig = px.scatter_map(
            blue_line_vehicles,
            lat="latitude",
            lon="longitude",
            hover_name="vehicle_id",
            hover_data=["route_id", "timestamp"],
            color_discrete_sequence=["blue"],
            zoom=10,
            height=600,
        )
        if unique_stops:
            fig.add_trace(
                go.Scattermap(
                    mode="lines+markers",
                    lon=[stop["lon"] for stop in unique_stops],
                    lat=[stop["lat"] for stop in unique_stops],
                    marker={"size": 8, "color": "gray"},
                    line=dict(width=3, color="gray"),
                    name="Blue Line Track",
                    text=[stop["description"] for stop in unique_stops],
                )
            )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return html.Div(
            [
                html.H3(f"Blue Line Train Map (Route ID: {blue_line_route_id})"),
                dcc.Graph(figure=fig),
            ]
        )
    else:
        return html.Div(
            [
                html.H3("Welcome to the Metro Transit Dashboard!"),
                html.P("Select a page from the navigation menu."),
            ]
        )


if __name__ == "__main__":
    app.run(debug=True)
