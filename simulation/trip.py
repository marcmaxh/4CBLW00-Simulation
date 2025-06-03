from .vehicle import Vehicle

class Trip:
    def __init__(self, vehicle: Vehicle, distance_km: float, traffic_level: int, passengers: int = 1):
        self.vehicle = vehicle
        self.distance_km = distance_km
        self.traffic_level = traffic_level
        self.passengers = passengers
        # Weather-related attributes (set externally by City)
        self.weather = None
        self.weather_speed_factor = 1.0
        self.weather_emission_factor = 1.0
        # Origin/destination (set externally by City)
        self.origin = None
        self.destination = None

        if passengers > self.vehicle.capacity:
            raise ValueError(f"Vehicle capacity exceeded: {passengers} > {self.vehicle.capacity}")

    def get_duration_hours(self) -> float:
        speed = self.vehicle.get_speed(self.traffic_level) * self.weather_speed_factor
        return self.distance_km / speed if speed > 0 else float('inf')

    def get_operational_emissions(self) -> float:
        return self.vehicle.emissions_per_km * self.distance_km * self.weather_emission_factor

    def get_total_emissions(self) -> float:
        return self.get_operational_emissions() + self.vehicle.embodied_emissions

    def get_emissions_per_passenger(self) -> float:
        return self.get_total_emissions() / self.passengers

    def summary(self) -> dict:
        return {
            "vehicle": self.vehicle.name,
            "origin": self.origin,
            "destination": self.destination,
            "distance_km": self.distance_km,
            "traffic_level": self.traffic_level,
            "weather": self.weather,
            "passengers": self.passengers,
            "speed_kmh": self.vehicle.get_speed(self.traffic_level) * self.weather_speed_factor,
            "duration_hr": self.get_duration_hours(),
            "emissions_total_g": self.get_total_emissions(),
            "emissions_per_passenger_g": self.get_emissions_per_passenger()
        }
