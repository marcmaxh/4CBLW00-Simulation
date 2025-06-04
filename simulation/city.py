import random
import os
import csv
from typing import List, Tuple
from .vehicle import FatBike, Car, Bus
from .trip import Trip
from .traffic_model import TrafficModel
from utils import traffic_api

class City:
    def __init__(self, name: str = "Eindhoven", seed: int = None, use_real_data: bool = False):
        self.name = name
        self.traffic_model = TrafficModel()
        self.zones = ["Centrum", "Strijp-S", "TU/e", "Woensel", "Tongelre", "Gestel"]
        self.use_real_data = use_real_data or (os.environ.get("USE_REAL_TRAFFIC", "0") == "1")

        # Load OD matrix from CSV
        self.od_matrix = self.load_od_matrix_from_csv()
        # Ensure bidirectionality for each mode
        new_od_matrix = {}
        for (src, dst), modes in self.od_matrix.items():
            new_od_matrix[(src, dst)] = modes
            new_od_matrix[(dst, src)] = modes
        self.od_matrix = new_od_matrix

        self.vehicles = [FatBike(), Car(), Bus()]

        self.traffic_profile = {
            "rush_hour": 80,
            "off_peak": 30,
            "night": 10
        }

        # Weather system: affects speed and emissions
        self.weather_types = ["clear", "rain", "snow", "fog"]
        self.weather_effects = {
            "clear": {"speed_factor": 1.0, "emission_factor": 1.0},
            "rain": {"speed_factor": 0.85, "emission_factor": 1.1},
            "snow": {"speed_factor": 0.7, "emission_factor": 1.2},
            "fog": {"speed_factor": 0.8, "emission_factor": 1.05},
        }

        if seed is not None:
            random.seed(seed)

    def load_od_matrix_from_csv(self):
        od_matrix = {}
        csv_path = 'simulation/Origin to POI.csv'
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            current_origin = None
            for row in reader:
                origin = row["Origin"].strip() if row["Origin"].strip() else current_origin
                if not origin:
                    continue
                current_origin = origin
                destination = row["Destination"].strip()
                if not destination:
                    continue
                try:
                    car_dist = float(row['Distance (by car, in km)']) if row['Distance (by car, in km)'] else None
                    bike_dist = float(row['Distance (by bike, in km)']) if row['Distance (by bike, in km)'] else None
                except Exception:
                    car_dist = None
                    bike_dist = None
                if car_dist is not None or bike_dist is not None:
                    od_matrix[(origin, destination)] = {"car": car_dist, "bike": bike_dist}
        return od_matrix

    def random_od_pair(self) -> Tuple[str, str]:
        return random.choice(list(self.od_matrix.keys()))

    def od_distance(self, origin: str, destination: str, mode: str = "car") -> float:
        if self.use_real_data:
            dist = traffic_api.get_real_distance(origin, destination)
            if dist:
                return dist
        d = self.od_matrix.get((origin, destination), None)
        if isinstance(d, dict):
            return d.get(mode, None)
        return d

    def random_traffic_level(self, origin: str, destination: str, time_of_day: str) -> int:
        if self.use_real_data:
            level = traffic_api.get_real_traffic(origin, destination)
            if level is not None:
                return level
        return self.traffic_model.get_traffic_level(origin, destination, time_of_day)

    def random_weather(self) -> str:
        # Weighted random: clear is most common
        return random.choices(self.weather_types, weights=[60, 25, 10, 5])[0]

    def generate_random_trip(self, time_of_day: str = "rush_hour") -> Trip:
        origin, destination = self.random_od_pair()
        vehicle = random.choice(self.vehicles)
        mode = "bike" if vehicle.name == "FatBike" else "car"
        distance = self.od_distance(origin, destination, mode)
        traffic = self.random_traffic_level(origin, destination, time_of_day)
        weather = self.random_weather()
        effects = self.weather_effects[weather]

        # More realistic passenger distribution
        if vehicle.name == "Bus":
            passengers = int(random.gauss(25, 10))
            passengers = max(5, min(vehicle.capacity, passengers))
        elif vehicle.name == "Car":
            passengers = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
        else:
            passengers = 1

        trip = Trip(vehicle, distance, traffic, passengers)
        trip.origin = origin
        trip.destination = destination
        trip.weather = weather
        trip.weather_speed_factor = effects["speed_factor"]
        trip.weather_emission_factor = effects["emission_factor"]
        return trip

