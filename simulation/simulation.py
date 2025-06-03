import random
from typing import List, Dict
from city import City
from vehicle import Car, Bus, FatBike
from utils import plotting


class Simulation:
    def __init__(self, city_name: str = "Eindhoven", num_trips: int = 100, seed: int = 42, use_real_data: bool = True):
        self.city = City(name=city_name, seed=seed, use_real_data=use_real_data)
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
        Returns a list of detailed trip summaries.
        """
        results = []
        for _ in range(self.num_trips):
            trip = self.city.generate_random_trip(time_of_day=self.time_of_day)
            results.append(trip.summary())
        return results

    def summarize_results(self, results: List[Dict]):
        """
        Summarize average metrics across all trips per vehicle type and report weather, occupancy, and delays.
        """
        from collections import Counter
        vehicle_stats = {}
        weather_counter = Counter()
        total_passengers = 0
        total_trips = len(results)
        total_delay = 0
        delay_threshold = 0.1  # hours, e.g., 6 minutes
        delayed_trips = 0

        for trip in results:
            v = trip['vehicle']
            vehicle_stats.setdefault(v, {'emissions': 0, 'duration': 0, 'count': 0, 'passengers': 0})
            vehicle_stats[v]['emissions'] += trip['emissions_total_g']
            vehicle_stats[v]['duration'] += trip['duration_hr']
            vehicle_stats[v]['count'] += 1
            vehicle_stats[v]['passengers'] += trip['passengers']
            weather_counter[trip['weather']] += 1
            total_passengers += trip['passengers']
            # Delay: if duration is more than expected for clear weather by threshold
            expected_speed = self.vehicles[v].get_speed(trip['traffic_level'])
            expected_time = trip['distance_km'] / expected_speed if expected_speed > 0 else float('inf')
            delay = trip['duration_hr'] - expected_time
            if delay > delay_threshold:
                delayed_trips += 1
                total_delay += delay

        print(f"\n--- Simulation Summary for {self.num_trips} trips ({self.time_of_day}) ---")
        for v, stats in vehicle_stats.items():
            avg_emissions = stats['emissions'] / stats['count']
            avg_time = stats['duration'] / stats['count']
            avg_occupancy = stats['passengers'] / stats['count']
            print(f"{v:8s} | Avg Emissions: {avg_emissions:.2f} g | Avg Time: {avg_time:.2f} h | Avg Occupancy: {avg_occupancy:.2f}")
        print(f"\nWeather distribution: {dict(weather_counter)}")
        print(f"Average passengers per trip: {total_passengers / total_trips:.2f}")
        if delayed_trips > 0:
            print(f"Delayed trips (>6min): {delayed_trips} ({100*delayed_trips/total_trips:.1f}%), Avg delay: {total_delay/delayed_trips*60:.1f} min")
        else:
            print("No significant delays detected.")

    def set_time_of_day(self, time_of_day: str):
        """
        Set the time of day for the simulation (affects traffic).
        """
        self.time_of_day = time_of_day


if __name__ == "__main__":
    sim = Simulation(num_trips=10000, use_real_data=False)
    sim.set_time_of_day("rush_hour")
    results = sim.run()
    sim.summarize_results(results)

    summary = plotting.summarize_for_plot(results)
    plotting.plot_summary(summary)
