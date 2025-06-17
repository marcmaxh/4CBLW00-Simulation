import matplotlib.pyplot as plt
from typing import List, Dict
from collections import Counter
import numpy as np

def summarize_for_plot(results: List[Dict]) -> Dict:
    """
    Summarizes emissions, time, weather, and delays per vehicle type.
    (Occupancy is not included in the summary.)
    """
    summary = {}
    weather_counter = Counter()
    duration_list = []
    delay_threshold = 0.1  # hours (6 min)
    delayed_trips = 0
    total_delay = 0
    for trip in results:
        v = trip["vehicle"]
        if v not in summary:
            summary[v] = {
                "total_emissions": 0,
                "total_time": 0,
                "total_emissions_per_passenger": 0,
                "count": 0
            }
        summary[v]["total_emissions"] += trip["emissions_total_g"]
        summary[v]["total_time"] += trip["duration_hr"]
        summary[v]["total_emissions_per_passenger"] += trip["emissions_per_passenger_g"]
        summary[v]["count"] += 1
        weather_counter[trip["weather"]] += 1
        duration_list.append(trip["duration_hr"])
        # Delay: if duration is more than expected for clear weather by threshold
        expected_time = trip["distance_km"] / trip["speed_kmh"] if trip["speed_kmh"] > 0 else float('inf')
        delay = trip["duration_hr"] - expected_time
        if delay > delay_threshold:
            delayed_trips += 1
            total_delay += delay

    # Compute averages
    for v in summary:
        summary[v]["avg_emissions"] = summary[v]["total_emissions"] / summary[v]["count"]
        summary[v]["avg_time"] = summary[v]["total_time"] / summary[v]["count"]
        summary[v]["avg_emissions_per_passenger"] = summary[v]["total_emissions_per_passenger"] / summary[v]["count"]
    summary["weather_distribution"] = dict(weather_counter)
    summary["duration_list"] = duration_list
    summary["delayed_trips"] = delayed_trips
    summary["total_trips"] = len(results)
    summary["avg_delay_min"] = (total_delay / delayed_trips * 60) if delayed_trips > 0 else 0
    return summary


def plot_summary(summary: Dict):
    """
    Plots average emissions, time, emissions per passenger, weather, and trip duration distribution.
    (Occupancy is not shown.)
    """
    vehicles = [v for v in summary if v not in ["weather_distribution", "duration_list", "delayed_trips", "total_trips", "avg_delay_min"]]
    avg_emissions = [summary[v]["avg_emissions"] for v in vehicles]
    avg_time = [summary[v]["avg_time"] for v in vehicles]
    avg_emissions_per_passenger = [summary[v]["avg_emissions_per_passenger"] for v in vehicles]
    weather_dist = summary["weather_distribution"]
    duration_list = summary["duration_list"]
    delayed_trips = summary["delayed_trips"]
    total_trips = summary["total_trips"]
    avg_delay_min = summary["avg_delay_min"]

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Simulation Results: Detailed Analysis")

    # Plot 1: Emissions
    axs[0, 0].bar(vehicles, avg_emissions, color=["#00a5cf", "#004e64", "#9fffcb"])
    axs[0, 0].set_title("Avg Emissions per Trip (g CO₂)")
    axs[0, 0].set_ylabel("Grams of CO₂")
    axs[0, 0].set_xlabel("Vehicle Type")

    # Plot 2: Time
    axs[0, 1].bar(vehicles, avg_time, color=["#00a5cf", "#004e64", "#9fffcb"])
    axs[0, 1].set_title("Avg Time per Trip (hours)")
    axs[0, 1].set_ylabel("Time (hours)")
    axs[0, 1].set_xlabel("Vehicle Type")

    # Plot 3: Emissions per Passenger
    axs[1, 0].bar(vehicles, avg_emissions_per_passenger, color=["#00a5cf", "#004e64", "#9fffcb"])
    axs[1, 0].set_title("Avg Emissions per Passenger (g CO₂)")
    axs[1, 0].set_ylabel("g CO₂ / Passenger")
    axs[1, 0].set_xlabel("Vehicle Type")

    # Plot 4: Weather distribution
    axs[1, 1].bar(weather_dist.keys(), weather_dist.values(), color=["#00a5cf", "#004e64", "#9fffcb", "#8187dc"][:len(weather_dist)])
    axs[1, 1].set_title("Weather Distribution")
    axs[1, 1].set_ylabel("Number of Trips")
    axs[1, 1].set_xlabel("Weather")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    # Print delay stats
    print(f"Delayed trips (>6min): {delayed_trips} / {total_trips} ({100*delayed_trips/total_trips:.1f}%), Avg delay: {avg_delay_min:.1f} min")

    return fig


def plot_distributions_per_vehicle(results: List[Dict]):
    """
    Plots distribution histograms for trip duration, emissions, and emissions per passenger per vehicle type.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from collections import defaultdict

    metrics = [
        ("duration_hr", "Trip Duration (hours)", "Duration (hours)"),
        ("emissions_total_g", "Total Emissions (g CO₂)", "Emissions (g CO₂)"),
        ("emissions_per_passenger_g", "Emissions per Passenger (g CO₂)", "Emissions per Passenger (g CO₂)")
    ]
    vehicle_types = set(trip["vehicle"] for trip in results)
    data = {metric: defaultdict(list) for metric, _, _ in metrics}
    for trip in results:
        for metric, _, _ in metrics:
            data[metric][trip["vehicle"]].append(trip[metric])

    fig, axs = plt.subplots(1, len(metrics), figsize=(6 * len(metrics), 5))
    if len(metrics) == 1:
        axs = [axs]
    colors = ["#00a5cf", "#004e64", "#9fffcb", "#8187dc"]
    for idx, (metric, title, xlabel) in enumerate(metrics):
        for i, v in enumerate(sorted(vehicle_types)):
            axs[idx].hist(data[metric][v], bins=20, alpha=0.6, label=v, color=colors[i % len(colors)])
        axs[idx].set_title(title)
        axs[idx].set_xlabel(xlabel)
        axs[idx].set_ylabel("Number of Trips")
        axs[idx].legend()
    plt.tight_layout()
    plt.show()
    return fig

