from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self, name:str, speed_kmh: float, emmisions_per_km: float, production_emission_kg: float, capacity: int = 1):
        self.name = name # Name of the vehicle
        self.speed_kmh = speed_kmh # Speed in km/h
        self.emmisions_per_km = emmisions_per_km # Average amount of C02 equivalent emissions per km (g*CO2/km)
        self.capacity = capacity # Number of passengers the vehicle can carry

    def get_emissions(self, distance_km: float) -> float:
        """
        Calculate the emissions for a given distance.
        """
        return self.emmisions_per_km * distance_km

    @abstractmethod
    def get_speed(self, traffic_leve: str) -> float:
        """
        Get the speed of the vehicle based on traffic level.
        """
        pass


class FatBike(Vehicle):
    def __init__(self):
        super().__init__(name="FatBike", speed_kmh=20, emmisions_per_km=1, production_emission_kg= 134)

    def get_speed(self, traffic_level: str) -> float:
        """
        Get the speed of the FatBike which is very lightly affected by traffic.
        """
        return self.speed_kmh * 0.9 if traffic_level == "heavy" else self.speed_kmh

class ECar(Vehicle):
    def __init__(self):
        super().__init__(name="ECar", speed_kmh=40, emmisions_per_km=20, production_emission_kg= 2000, capacity=2)

    def get_speed(self, traffic_level: str) -> float:
        """
        Get the speed of the ECar which is affected by traffic.
        """
        if traffic_level == "low":
            return self.speed_kmh
        elif traffic_level == "medium":
            return self.speed_kmh * 0.75
        elif traffic_level == "heavy":
            return self.speed_kmh * 0.5
        else:
            return self.speed_kmh # Default to normal speed if traffic level is unknown

class Car(Vehicle):
    def __init__(self):
        super().__init__(name="Car", speed_kmh=60, emmisions_per_km=150, production_emission_kg= 5000, capacity=4)
