from abc import ABC, abstractmethod
from config.vehicle_config import vehicle_config

class Vehicle(ABC):
    def __init__(self, name:str, speed_kmh: float, emissions_per_km: float, embodied_emissions: float, capacity: int = 1):
        self.name = name # Name of the vehicle
        self.speed_kmh = speed_kmh # Speed in km/h
        self.emissions_per_km = emissions_per_km # Average amount of C02 equivalent emissions per km (g*CO2/km)
        self.embodied_emissions = embodied_emissions # Production emissions in kg
        self.capacity = capacity # Number of passengers the vehicle can carry

    def get_emissions(self, distance_km: float) -> float:
        """
        Calculate the emissions for a given distance.
        """
        return self.emissions_per_km * distance_km + self.embodied_emissions

    @abstractmethod
    def get_speed(self, traffic_level: str) -> float:
        """
        Get the speed of the vehicle based on traffic level.
        """
        pass


class FatBike(Vehicle):
    def __init__(self):
        cfg = vehicle_config["FatBike"]
        super().__init__(
            name=cfg["name"],
            speed_kmh=cfg["base_speed_kmh"],
            emissions_per_km=cfg["emissions_per_km"],
            embodied_emissions=cfg["embodied_emissions"],
            capacity=cfg["capacity"]
        )

    def get_speed(self, traffic_level: int) -> float:
        """
        FatBike slows down by 1% for every 5% traffic increase, capped at 30% reduction.
        """
        if traffic_level > 0:
            speed_reduction = max(0.3, 0.01 * (traffic_level // 5))
            return self.speed_kmh * (1 - speed_reduction)
        return self.speed_kmh


class Car(Vehicle):
    def __init__(self):
        super().__init__(name="Car", speed_kmh=60, emissions_per_km=150, embodied_emissions= 5000, capacity=4)

    def get_speed(self, traffic_level: int) -> float:
        """
        Get the speed of the Car which has to slow down by 1% for every 1% increase in traffic level
        with a minimum average speed reduction of 60%
        """
        if traffic_level > 0:
            speed_reduction = max(0.6, 0.01 * traffic_level)
            return self.speed_kmh * (1 - speed_reduction)
        return self.speed_kmh

class Bus(Vehicle):
    def __init__(self):
        super().__init__(name="Bus", speed_kmh=40, emissions_per_km=90, embodied_emissions= 20000, capacity=50)

    def get_speed(self, traffic_level: int) -> float:
        """
        Get the speed of the Bus which has to slow down by 1% for every 2% increase in traffic level
        with a minimum average speed reduction of 50%
        """
        if traffic_level > 0:
            speed_reduction = max(0.5, 0.01 * (traffic_level // 2))
            return self.speed_kmh * (1 - speed_reduction)
        return self.speed_kmh

