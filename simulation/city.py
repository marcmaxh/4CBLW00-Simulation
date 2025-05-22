import random
from typing import List, Tuple
from vehicle import FatBike, Car, Bus
from trip import Trip
from traffic_model import TrafficModel

class City:
    def __init__(self, name: str = "Eindhoven", seed: int = None):
        self.name = name
        self.traffic_model = TrafficModel()
        self.zones = ["Centrum", "Strijp-S", "TU/e", "Woensel", "Tongelre", "Gestel"]

        # Example static OD matrix (distances in km)
        self.od_matrix = {
            ("Centrum", "Strijp-S"): 2.0,
            ("Centrum", "TU/e"): 2.5,
            ("Centrum", "Woensel"): 4.0,
            ("Centrum", "Tongelre"): 3.2,
            ("Centrum", "Gestel"): 3.8,
        }

        # Ensure bidirectionality
        self.od_matrix.update({(dst, src): dist for (src, dst), dist in self.od_matrix.items()})

        self.vehicles = [FatBike(), Car(), Bus()]

        self.traffic_profile = {
            "rush_hour": 80,
            "off_peak": 30,
            "night": 10
        }

        if seed is not None:
            random.seed(seed)

    def random_od_pair(self) -> Tuple[str, str]:
        return random.choice(list(self.od_matrix.keys()))

    def od_distance(self, origin: str, destination: str) -> float:
        return self.od_matrix.get((origin, destination), None)

    def random_traffic_level(self, origin: str, destination: str, time_of_day: str) -> int:
        return self.traffic_model.get_traffic_level(origin, destination, time_of_day)

    def generate_random_trip(self, time_of_day: str = "rush_hour") -> Trip:
        origin, destination = self.random_od_pair()
        distance = self.od_distance(origin, destination)
        traffic = self.random_traffic_level(origin, destination, time_of_day)
        vehicle = random.choice(self.vehicles)

        if vehicle.name == "Bus":
            passengers = random.randint(10, vehicle.capacity)
        elif vehicle.name == "Car":
            passengers = random.randint(1, vehicle.capacity)
        else:
            passengers = 1

        trip = Trip(vehicle, distance, traffic, passengers)
        trip.origin = origin
        trip.destination = destination
        return trip

    def generate_many_trips(self, n: int, time_of_day: str = "rush_hour") -> List[Trip]:
        return [self.generate_random_trip(time_of_day) for _ in range(n)]

    def simulate_trips(self, n: int, time_of_day: str = "rush_hour") -> List[dict]:
        trips = self.generate_many_trips(n, time_of_day)
        return [trip.summary() for trip in trips]
