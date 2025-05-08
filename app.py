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
                dcc.Link("Routes", href="/routes"),
                html.Br(),
                dcc.Link("Map", href="/map"),
                html.Br(),
                dcc.Link("Blue Line Map", href="/blue-line-map"),
                html.Br(),
                dcc.Link("Green Line Map", href="/green-line-map"),
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
    elif pathname == "/blue-line-map":
        import json
        import plotly.express as px
        import plotly.graph_objects as go

        # Load static Blue Line stops from JSON
        with open("assets/901_stops.json", "r", encoding="utf-8") as f:
            blue_line_stops = json.load(f)
        # Sort stops by direction and then by their order in the file (as listed)
        # Optionally, you could sort by latitude/longitude if needed
        # Get Blue Line vehicles from GTFS realtime
        vehicles = fetch_vehicle_positions()
        blue_line_vehicles = [v for v in vehicles if v.get("route_id") == "901"]
        fig = px.scatter_map(
            blue_line_vehicles,
            lat="latitude",
            lon="longitude",
            hover_name="vehicle_id",
            hover_data=["route_id", "timestamp"],
            color_discrete_sequence=["blue"],
            zoom=11,
            height=600,
        )
        # Draw the Blue Line track using the static stops (direction 0 as default)
        stops_dir0 = [s for s in blue_line_stops if s["direction_id"] == 0]
        fig.add_trace(
            go.Scattermap(
                mode="lines+markers",
                lon=[stop["longitude"] for stop in stops_dir0],
                lat=[stop["latitude"] for stop in stops_dir0],
                marker={"size": 10, "color": "darkblue", "symbol": "circle"},
                line=dict(width=3, color="royalblue"),
                name="Blue Line Track (Northbound)",
                text=[stop["description"] for stop in stops_dir0],
            )
        )
        # Optionally, add direction 1 as a separate line
        stops_dir1 = [s for s in blue_line_stops if s["direction_id"] == 1]
        if stops_dir1:
            fig.add_trace(
                go.Scattermap(
                    mode="lines+markers",
                    lon=[stop["longitude"] for stop in stops_dir1],
                    lat=[stop["latitude"] for stop in stops_dir1],
                    marker={"size": 8, "color": "blue"},
                    line=dict(width=2, color="blue"),
                    name="Blue Line Track (Southbound)",
                    text=[stop["description"] for stop in stops_dir1],
                )
            )
        # Draw trains as a separate scatter layer over the tracks
        if blue_line_vehicles:
            fig.add_trace(
                go.Scattermap(
                    mode="markers",
                    lon=[v["longitude"] for v in blue_line_vehicles],
                    lat=[v["latitude"] for v in blue_line_vehicles],
                    marker={"size": 14, "color": "blue", "symbol": "rail"},
                    name="Blue Line Trains",
                    text=[
                        f"Train {v.get('vehicle_id', 'N/A')}<br>Last seen: {v.get('timestamp', 'N/A')}"
                        for v in blue_line_vehicles
                    ],
                )
            )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return html.Div(
            [
                html.H3("Blue Line Train Map"),
                dcc.Graph(figure=fig),
            ]
        )
    elif pathname == "/green-line-map":
        import json
        import plotly.express as px
        import plotly.graph_objects as go

        # Load static Green Line stops from JSON
        with open("assets/902_stops.json", "r", encoding="utf-8") as f:
            green_line_stops = json.load(f)
        # Get Green Line vehicles from GTFS realtime
        vehicles = fetch_vehicle_positions()
        green_line_vehicles = [v for v in vehicles if v.get("route_id") == "902"]
        fig = px.scatter_map(
            green_line_vehicles,
            lat="latitude",
            lon="longitude",
            hover_name="vehicle_id",
            hover_data=["route_id", "timestamp"],
            color_discrete_sequence=["green"],
            zoom=12,
            height=600,
        )
        # Draw the Green Line track using the static stops (direction 0 as default)
        stops_dir0 = [s for s in green_line_stops if s["direction_id"] == 0]
        fig.add_trace(
            go.Scattermap(
                mode="lines+markers",
                lon=[stop["longitude"] for stop in stops_dir0],
                lat=[stop["latitude"] for stop in stops_dir0],
                marker={"size": 8, "color": "green"},
                line=dict(width=3, color="green"),
                name="Green Line Track (Eastbound)",
                text=[stop["description"] for stop in stops_dir0],
            )
        )
        # Optionally, add direction 1 as a separate line
        stops_dir1 = [s for s in green_line_stops if s["direction_id"] == 1]
        if stops_dir1:
            fig.add_trace(
                go.Scattermap(
                    mode="lines+markers",
                    lon=[stop["longitude"] for stop in stops_dir1],
                    lat=[stop["latitude"] for stop in stops_dir1],
                    marker={"size": 8, "color": "green"},
                    line=dict(width=2, color="green"),
                    name="Green Line Track (Westbound)",
                    text=[stop["description"] for stop in stops_dir1],
                )
            )
        # Draw trains as a separate scatter layer over the tracks
        if green_line_vehicles:
            fig.add_trace(
                go.Scattermap(
                    mode="markers",
                    lon=[v["longitude"] for v in green_line_vehicles],
                    lat=[v["latitude"] for v in green_line_vehicles],
                    marker={"size": 14, "color": "green", "symbol": "rail"},
                    name="Green Line Trains",
                    text=[
                        f"Train {v.get('vehicle_id', 'N/A')}<br>Last seen: {v.get('timestamp', 'N/A')}"
                        for v in green_line_vehicles
                    ],
                )
            )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return html.Div(
            [
                html.H3("Green Line Train Map"),
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
