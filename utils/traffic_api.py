# import requests
import os

# You need to get a free API key from https://openrouteservice.org/
ORS_API_KEY = os.environ.get("ORS_API_KEY", "YOUR_ORS_API_KEY_HERE")
ORS_BASE_URL = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"

# Example coordinates for zones (Eindhoven, adjust as needed)
ZONE_COORDS = {
    "Centrum": [5.4791, 51.4416],
    "Strijp-S": [5.4631, 51.4461],
    "TU/e": [5.4866, 51.4485],
    "Woensel": [5.4700, 51.4700],
    "Tongelre": [5.5110, 51.4380],
    "Gestel": [5.4570, 51.4230],
}

def get_real_distance(origin: str, destination: str) -> float:
    """
    Returns the real-world driving distance (in km) between two zones using OpenRouteService.
    """
    if origin not in ZONE_COORDS or destination not in ZONE_COORDS:
        return None
    coords = [ZONE_COORDS[origin], ZONE_COORDS[destination]]
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": coords}
    try:
        resp = requests.post(ORS_BASE_URL, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Distance in meters (GeoJSON response)
        meters = data["features"][0]["properties"]["segments"][0]["distance"]
        return meters / 1000.0
    except Exception as e:
        print(f"[ORS] Error fetching distance: {e}")
        return None

def get_real_traffic(origin: str, destination: str) -> int:
    """
    Returns a traffic level (0-100) based on travel duration vs. free-flow duration.
    """
    if origin not in ZONE_COORDS or destination not in ZONE_COORDS:
        return 50
    coords = [ZONE_COORDS[origin], ZONE_COORDS[destination]]
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {"coordinates": coords}
    try:
        resp = requests.post(ORS_BASE_URL, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        segment = data["features"][0]["properties"]["segments"][0]
        duration = segment["duration"]  # seconds
        distance = segment["distance"]  # meters
        # Assume free-flow speed = 50 km/h
        free_flow = (distance / 1000) / 50 * 3600
        traffic_level = min(100, max(0, int(100 * (duration / free_flow - 1))))
        return traffic_level
    except Exception as e:
        print(f"[ORS] Error fetching traffic: {e}")
        return 50

