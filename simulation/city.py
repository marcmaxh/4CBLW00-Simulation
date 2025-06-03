import random
import os
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

        # Expanded OD matrix (distances in km, more pairs)
        self.od_matrix = {

            # Origin Wielewaal
            ("Wielewaal", "Airport"): 6.5,
            ("Wielewaal", "Meerhoven shopping center"): 4.2,
            ("Wielewaal", "High Tech Campus"): 8.1,
            ("Wielewaal", "Eindhoven City Centre"): 7.0,
            ("Wielewaal", "Eindhoven Station Strijp-S"): 6.8,
            ("Wielewaal", "Flight Forum"): 5.7,
            ("Wielewaal", "SintLucas"): 7.3,
            ("Wielewaal", "TU/e"): 8.5,
            ("Wielewaal", "Medisch Centrum Boschdijk"): 5.9,
            ("Wielewaal", "Obs de Opbouw"): 4.8,

            # Origin Barrier
            ("Barrier", "Airport"): 7.2,
            ("Barrier", "Eindhoven City Centre"): 3.5,
            ("Barrier", "Eindhoven Station Strijp S"): 4.0,
            ("Barrier", "Winkelcentrum Woensel"): 5.1,
            ("Barrier", "Flight Forum"): 6.0,
            ("Barrier", "High Tech Campus"): 7.8,
            ("Barrier", "Antoon Schellenscollege"): 2.9,
            ("Barrier", "TU/e"): 4.3,
            ("Barrier", "Medisch Centrum Boschdijk"): 5.5,
            ("Barrier", "Obs de Opbouw"): 6.2,

            # Origin Muscherg, Geestenberg
            ("Muscherg", "Airport"): 8.0,
            ("Muscherg", "Eindhoven City Centre"): 4.5,
            ("Muscherg", "Eindhoven Central Station"): 5.0,
            ("Muscherg", "De Kade"): 3.8,
            ("Muschberg", "High Tech Campus"): 6.5,
            ("Muscherg", "Lorentz Casimir Lyceum"): 4.2,
            ("Muscherg", "Flight Forum"): 7.0,
            ("Muscherg", "TU/e"): 5.8,
            ("Muscherg", "Stroomz Tongelre"): 4.0,
            ("Muscherg", "BS 't Karregat Omnio"): 3.5,

            # Origin Esp
            ("Esp", "Airport"): 10.2,
            ("Esp", "Eindhoven City Centre"): 6.7,
            ("Esp", "Eindhoven Central Station"): 7.1,
            ("Esp", "Het Facilitair Gezondheidscentrum"): 2.3,
            ("Esp", "De Handreiking"): 3.0,

            # Origin Sintenbuurt
            ("Sintenbuurt", "High Tech Campus"): 5.4,
            ("Sintenbuurt", "Eindhoven City Centre"): 2.1,
            ("Sintenbuurt", "TU/e"): 3.2,
            ("Sintenbuurt", "Airport"): 8.7,
            ("Sintenbuurt", "Eindhoven Central Station"): 2.5,
            ("Sintenbuurt", "Augustinianum"): 1.8,
            ("Sintenbuurt", "Stroomz Stratum"): 2.9,
            ("Sintenbuurt", "Bs de Klimboom"): 2.6,

        }

        # Ensure bidirectionality
        self.od_matrix.update({(dst, src): dist for (src, dst), dist in self.od_matrix.items()})

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

    def random_od_pair(self) -> Tuple[str, str]:
        return random.choice(list(self.od_matrix.keys()))

    def od_distance(self, origin: str, destination: str) -> float:
        if self.use_real_data:
            dist = traffic_api.get_real_distance(origin, destination)
            if dist:
                return dist
        return self.od_matrix.get((origin, destination), None)

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
        distance = self.od_distance(origin, destination)
        traffic = self.random_traffic_level(origin, destination, time_of_day)
        vehicle = random.choice(self.vehicles)
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

    def generate_many_trips(self, n: int, time_of_day: str = "rush_hour") -> List[Trip]:
        return [self.generate_random_trip(time_of_day) for _ in range(n)]

    def simulate_trips(self, n: int, time_of_day: str = "rush_hour") -> List[dict]:
        trips = self.generate_many_trips(n, time_of_day)
        return [trip.summary() for trip in trips]
