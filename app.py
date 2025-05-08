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
server = app.server # Expose server for Gunicorn or other WSGI servers

# Define the layout of the application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1("Metro Transit Dashboard"),
    html.Nav([
        dcc.Link('Home', href='/'),
        html.Br(),
        dcc.Link('Trip Updates', href='/trip-updates'),
        html.Br(),
        dcc.Link('Service Alerts', href='/service-alerts'),
        html.Br(),
        dcc.Link('Vehicle Positions', href='/vehicle-positions'),
        html.Br(),
        dcc.Link('Map', href='/map'),
        html.Br(),
        dcc.Link('Routes', href='/routes'),
    ]),
    html.Hr(),
    html.Div(id='page-content')
])

# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/trip-updates':
        updates = get_trip_updates()
        return html.Div([
            html.H3('Trip Updates'),
            # Displaying as a simple list for now, can be improved with a table or other components
            html.Ul([html.Li(f"{update['trip_id']} - Route: {update['route_id']} - Arrival: {update['arrival']}") for update in updates])
        ])
    elif pathname == '/service-alerts':
        alerts = fetch_service_alerts()
        return html.Div([
            html.H3('Service Alerts'),
            html.Ul([html.Li(f"{alert.get('header', 'N/A')}: {alert.get('description', 'N/A')}") for alert in alerts])
        ])
    elif pathname == '/vehicle-positions':
        vehicles = fetch_vehicle_positions()
        return html.Div([
            html.H3('Vehicle Positions'),
            html.Ul([html.Li(f"Vehicle {vehicle['vehicle_id']} on route {vehicle['route_id']} at ({vehicle['latitude']}, {vehicle['longitude']}) at {vehicle['timestamp']}") for vehicle in vehicles])
        ])
    elif pathname == '/map':
        vehicles = fetch_vehicle_positions()
        # Basic map using Plotly Express (requires plotly to be installed)
        # For a more interactive map, consider dash-leaflet or other mapping libraries
        if vehicles and 'error' not in vehicles[0]:
            import plotly.express as px
            df = px.data.tips() # Placeholder for actual vehicle data processing for map
            # Create a scatter_mapbox plot
            # This requires a Mapbox access token for some map styles.
            # Using 'open-street-map' style which doesn't require a token.
            fig = px.scatter_map(vehicles, lat="latitude", lon="longitude", 
                                    hover_name="vehicle_id", 
                                    hover_data=["route_id", "timestamp"],
                                    color_discrete_sequence=["blue"],
                                    zoom=10, height=600)
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            return html.Div([html.H3('Map View'), dcc.Graph(figure=fig)])
        else:
            return html.Div([html.H3('Map View'), html.P('Could not load vehicle data for the map.')])
    elif pathname == '/routes':
        api = MetroTransitAPI()
        routes_data = api.get_routes()
        return html.Div([
            html.H3('Routes'),
            html.Ul([html.Li(f"{route['route_label']} (ID: {route['route_id']})") for route in routes_data])
        ])
    else:
        return html.Div([
            html.H3('Welcome to the Metro Transit Dashboard!'),
            html.P('Select a page from the navigation menu.')
        ])

if __name__ == '__main__':
    app.run(debug=True)
