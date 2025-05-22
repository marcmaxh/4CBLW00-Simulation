from typing import Dict

class TrafficModel:
    def __init__(self):
        # Default traffic levels by time of day (0–100 scale)
        self.time_based_traffic = {
            "night": 10,
            "off_peak": 30,
            "midday": 50,
            "rush_hour": 80
        }

        # Optional override: specific traffic levels per zone and time
        self.zone_traffic_profile: Dict[str, Dict[str, int]] = {}

    def set_zone_traffic(self, zone: str, time_of_day: str, level: int):
        """
        Manually set traffic level for a zone and time.
        """
        if zone not in self.zone_traffic_profile:
            self.zone_traffic_profile[zone] = {}
        self.zone_traffic_profile[zone][time_of_day] = level

    def get_traffic_level(self, origin: str, destination: str, time_of_day: str) -> int:
        """
        Return average traffic level between two zones at a given time.
        Defaults to time-based traffic if no zone-specific override exists.
        """
        origin_level = self.zone_traffic_profile.get(origin, {}).get(time_of_day)
        dest_level = self.zone_traffic_profile.get(destination, {}).get(time_of_day)

        if origin_level is not None and dest_level is not None:
            return int((origin_level + dest_level) / 2)
        elif origin_level is not None:
            return origin_level
        elif dest_level is not None:
            return dest_level
        else:
            return self.time_based_traffic.get(time_of_day, 50)
