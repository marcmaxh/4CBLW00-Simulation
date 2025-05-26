from .vehicle import Vehicle

class Trip:
    def __init__(self, vehicle: Vehicle, distance_km: float, traffic_level: int, passengers: int = 1):
        self.vehicle = vehicle
        self.distance_km = distance_km
        self.traffic_level = traffic_level
        self.passengers = passengers

        if passengers > self.vehicle.capacity:
            raise ValueError(f"Vehicle capacity exceeded: {passengers} > {self.vehicle.capacity}")

    def get_duration_hours(self) -> float:
        speed = self.vehicle.get_speed(self.traffic_level)
        return self.distance_km / speed if speed > 0 else float('inf')

    def get_operational_emissions(self) -> float:
        return self.vehicle.emissions_per_km * self.distance_km

    def get_total_emissions(self) -> float:
        return self.get_operational_emissions() + self.vehicle.production_emission_kg

    def get_emissions_per_passenger(self) -> float:
        return self.get_total_emissions() / self.passengers

    def summary(self) -> dict:
        return {
            "vehicle": self.vehicle.name,
            "distance_km": self.distance_km,
            "traffic_level": self.traffic_level,
            "speed_kmh": self.vehicle.get_speed(self.traffic_level),
            "duration_hr": self.get_duration_hours(),
            "emissions_total_g": self.get_total_emissions(),
            "emissions_per_passenger_g": self.get_emissions_per_passenger()
        }
