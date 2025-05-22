import random
from typing import List, Dict
from city import City
from trip import Trip
from vehicle import Car, Bus, FatBike
from utils import plotting


class Simulation:
    def __init__(self, city_name: str = "Eindhoven", num_trips: int = 100, seed: int = 42):
        self.city = City(name=city_name, seed=seed)
        self.num_trips = num_trips
        self.time_of_day = "rush_hour"  # default; can be changed dynamically
        self.vehicles = {
            "Car": Car(),
            "Bus": Bus(),
            "FatBike": FatBike()
        }

    def run(self) -> List[Dict]:
        """
        Run the simulation for a number of random trips.
        Returns a list of trip metrics per vehicle type.
        """
        results = []

        for _ in range(self.num_trips):
            trip = self.city.generate_random_trip(time_of_day=self.time_of_day)
            trip_data = {
                "origin": trip.origin,
                "destination": trip.destination,
                "distance_km": trip.distance_km,
                "traffic_level": trip.traffic_level,
                "results": {}
            }

            for name, vehicle in self.vehicles.items():
                emissions = vehicle.get_emissions(trip.distance_km)
                speed = vehicle.get_speed(trip.traffic_level)
                time_hr = trip.distance_km / speed if speed > 0 else float("inf")

                trip_data["results"][name] = {
                    "emissions_g": round(emissions, 2),
                    "speed_kmh": round(speed, 2),
                    "time_hr": round(time_hr, 2)
                }

            results.append(trip_data)

        return results

    def summarize_results(self, results: List[Dict]):
        """
        Summarize average metrics across all trips per vehicle type.
        """
        summary = {name: {"total_emissions": 0, "total_time": 0, "count": 0}
                   for name in self.vehicles.keys()}

        for trip in results:
            for vehicle, data in trip["results"].items():
                summary[vehicle]["total_emissions"] += data["emissions_g"]
                summary[vehicle]["total_time"] += data["time_hr"]
                summary[vehicle]["count"] += 1

        print(f"\n--- Simulation Summary for {self.num_trips} trips ({self.time_of_day}) ---")
        for vehicle, data in summary.items():
            count = data["count"]
            avg_emissions = data["total_emissions"] / count
            avg_time = data["total_time"] / count
            print(f"{vehicle:8s} | Avg Emissions: {avg_emissions:.2f} g | Avg Time: {avg_time:.2f} h")

    def set_time_of_day(self, time_of_day: str):
        """
        Set the time of day for the simulation (affects traffic).
        """
        self.time_of_day = time_of_day


if __name__ == "__main__":
    sim = Simulation(num_trips=100)
    sim.set_time_of_day("rush_hour")
    results = sim.run()
    sim.summarize_results(results)

    summary = plotting.summarize_for_plot(results)
    plotting.plot_summary(summary)
