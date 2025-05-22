import matplotlib.pyplot as plt
from typing import List, Dict


def summarize_for_plot(results: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Summarizes emissions and time per vehicle type.
    """
    summary = {}
    for trip in results:
        for vehicle, data in trip["results"].items():
            if vehicle not in summary:
                summary[vehicle] = {
                    "total_emissions": 0,
                    "total_time": 0,
                    "count": 0
                }
            summary[vehicle]["total_emissions"] += data["emissions_g"]
            summary[vehicle]["total_time"] += data["time_hr"]
            summary[vehicle]["count"] += 1

    # Compute averages
    for vehicle in summary:
        summary[vehicle]["avg_emissions"] = summary[vehicle]["total_emissions"] / summary[vehicle]["count"]
        summary[vehicle]["avg_time"] = summary[vehicle]["total_time"] / summary[vehicle]["count"]

    return summary


def plot_summary(summary: Dict[str, Dict[str, float]]):
    """
    Plots average emissions and average time per vehicle type.
    """
    vehicles = list(summary.keys())
    avg_emissions = [summary[v]["avg_emissions"] for v in vehicles]
    avg_time = [summary[v]["avg_time"] for v in vehicles]

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Simulation Results by Vehicle Type")

    # Plot 1: Emissions
    axs[0].bar(vehicles, avg_emissions, color=["red", "blue", "green"])
    axs[0].set_title("Average Emissions per Trip (g CO₂)")
    axs[0].set_ylabel("Grams of CO₂")
    axs[0].set_xlabel("Vehicle Type")

    # Plot 2: Time
    axs[1].bar(vehicles, avg_time, color=["red", "blue", "green"])
    axs[1].set_title("Average Time per Trip (hours)")
    axs[1].set_ylabel("Time (hours)")
    axs[1].set_xlabel("Vehicle Type")

    plt.tight_layout()
    plt.show()
