import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# Import data fetching functions from other modules
# These will be used in callbacks later
from trip_updates import get_trip_updates
from service_alerts import fetch_service_alerts
from vehicle_position import fetch_vehicle_positions
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
        routes_data = api.get_routes()
        blue_line_route_id = None
        for route in routes_data:
            if "Blue Line" in route.get("route_label", ""):
                blue_line_route_id = route.get("route_id")
                break
        if not blue_line_route_id:
            return html.Div(
                [
                    html.H3("Blue Line Train Map"),
                    html.P("Could not find the Blue Line route ID."),
                ]
            )
        vehicles = fetch_vehicle_positions()
        blue_line_vehicles = []
        if vehicles and (
            isinstance(vehicles, list) and (not vehicles or "error" not in vehicles[0])
        ):
            for vehicle in vehicles:
                if vehicle.get("route_id") == blue_line_route_id:
                    blue_line_vehicles.append(vehicle)
        if blue_line_vehicles:
            import plotly.express as px
            import plotly.graph_objects as go

            blue_line_track_lat = [44.9778, 44.9760, 44.9730, 44.9700, 44.9670]
            blue_line_track_lon = [-93.2650, -93.2600, -93.2550, -93.2500, -93.2450]
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
            fig.add_trace(
                go.Scattermap(
                    mode="lines",
                    lon=blue_line_track_lon,
                    lat=blue_line_track_lat,
                    marker={"size": 0},
                    line=dict(width=2, color="gray"),
                    name="Blue Line Track",
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
        elif (
            vehicles
            and isinstance(vehicles, list)
            and vehicles
            and "error" in vehicles[0]
        ):
            return html.Div(
                [
                    html.H3("Blue Line Train Map"),
                    html.P("Could not load vehicle data for the map."),
                ]
            )
        else:
            return html.Div(
                [
                    html.H3(f"Blue Line Train Map (Route ID: {blue_line_route_id})"),
                    html.P("No Blue Line trains currently active or data unavailable."),
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
