# 🚇 Metro Transit Dashboard 🚌

A comprehensive dashboard application for monitoring the Metro Transit system in Minneapolis/St. Paul, MN. This project provides real-time tracking of transit vehicles, service alerts, and route information using Metro Transit's GTFS and NexTrip APIs.

## 🛠️ Installation

```shell
# Clone the repository
git clone https://github.com/semanticdata/metro-transit-dashboard.git
cd metro-transit-dashboard

# Install dependencies
pip install -r requirements.txt
```

## 📊 Features

- Real-time vehicle tracking
- Service alerts monitoring
- Trip updates and schedules
- Route information and stop locations
- Interactive maps for transit lines

## 🚀 Usage

### Data Extraction Scripts

#### Extract GTFS Data

The `extract_gtfs_data.py` script fetches real-time data from Metro Transit's GTFS feeds:

```shell
python extract_gtfs_data.py
```

This script extracts:

- Vehicle positions (location, speed, route info)
- Service alerts (delays, detours, disruptions)
- Trip updates (arrival/departure times)

Data is saved in JSON format in the `data` directory with timestamps.

#### Get Route Stops

The `get_route_stops.py` script retrieves detailed information about stops for a specific route:

```shell
python get_route_stops.py {route_id} {output.json}
```

Example:

```shell
python get_route_stops.py 901 blue_line_stops.json
```

This generates a JSON file containing:

- Stop locations (latitude/longitude)
- Stop descriptions
- Place codes
- Direction information

## 🔗 API Reference

### Metro Transit APIs

- GTFS Realtime API: <https://svc.metrotransit.org/>
- Trip Updates feed: <https://svc.metrotransit.org/mtgtfs/tripupdates.pb>
- Vehicle Positions feed: <https://svc.metrotransit.org/mtgtfs/vehiclepositions.pb>
- Service Alerts feed: <https://svc.metrotransit.org/mtgtfs/alerts.pb>
- NexTrip API Swagger UI: <https://svc.metrotransit.org/swagger/index.html>
- API Reference: <https://svc.metrotransit.org/swagger/docs/v2/nextrip>

### API Endpoints

#### `/nextrip/{route_id}/{direction_id}/{place_code}`

```json
{
  "stops": [
    {
      "stop_id": 0,
      "latitude": 0,
      "longitude": 0,
      "description": "string"
    }
  ],
  "alerts": [
    {
      "stop_closed": true,
      "alert_text": "string"
    }
  ],
  "departures": [
    {
      "actual": true,
      "trip_id": "string",
      "stop_id": 0,
      "departure_text": "string",
      "departure_time": 0,
      "description": "string",
      "gate": "string",
      "route_id": "string",
      "route_short_name": "string",
      "direction_id": 0,
      "direction_text": "string",
      "terminal": "string",
      "agency_id": 0,
      "schedule_relationship": "string"
    }
  ]
}
```

#### `/nextrip/{stop_id}`

```json
{
  "stops": [
    {
      "stop_id": 0,
      "latitude": 0,
      "longitude": 0,
      "description": "string"
    }
  ],
  "alerts": [
    {
      "stop_closed": true,
      "alert_text": "string"
    }
  ],
  "departures": [
    {
      "actual": true,
      "trip_id": "string",
      "stop_id": 0,
      "departure_text": "string",
      "departure_time": 0,
      "description": "string",
      "gate": "string",
      "route_id": "string",
      "route_short_name": "string",
      "direction_id": 0,
      "direction_text": "string",
      "terminal": "string",
      "agency_id": 0,
      "schedule_relationship": "string"
    }
  ]
}
```

#### `/nextrip/agencies`

```json
[
  {
    "agency_id": 0,
    "agency_name": "string"
  }
]
```

#### `/nextrip/directions/{route_id}`

```json
[
  {
    "direction_id": 0,
    "direction_name": "string"
  }
]
```

#### `/nextrip/routes`

```json
[
  {
    "route_id": "string",
    "agency_id": 0,
    "route_label": "string"
  }
]
```

#### `/nextrip/stops/{route_id}/{direction_id}`

```json
[
  {
    "place_code": "string",
    "description": "string"
  }
]
```

#### `/nextrip/vehicles/{route_id}`

```json
[
  {
    "trip_id": "string",
    "direction_id": 0,
    "direction": "string",
    "location_time": 0,
    "route_id": "string",
    "terminal": "string",
    "latitude": 0,
    "longitude": 0,
    "bearing": 0,
    "odometer": 0,
    "speed": 0
  }
]
```
