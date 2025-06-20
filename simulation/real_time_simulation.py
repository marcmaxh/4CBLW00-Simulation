import json
import time
import random
import logging
from collections import deque, defaultdict
from typing import Dict, List
from .city import City
from .trip import Trip
import matplotlib.pyplot as plt

TIME_BLOCKS = [
    ("morning_peak", "07:00", "09:30"),
    ("midday_offpeak", "9:30", "15:30"),
    ("evening_peak", "15:30", "18:30"),
    ("evening_offpeak", "18:30", "22:00"),
    ("night", "22:00", "7:00")
]

class RealTimeSimulation:
    def __init__(self, demand_json_path: str = "data/daily_demand.json", seed: int = 42, timeout_min: int = 5, cancel_prob: float = 0.8):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger("RealTimeSimulation")
        self.city = City(seed=seed)
        self.timeout_min = timeout_min
        self.cancel_prob = cancel_prob
        with open(demand_json_path, "r") as f:
            self.demand = json.load(f)["time_blocks"]
        self.day_minutes = 24 * 60
        self.scenarios = ["optimistic", "moderate", "pessimistic"]
        self.stats = {s: {"wait_times": [], "serviced": 0, "unsuccessful": 0, "total": 0} for s in self.scenarios}
        self.queues = {s: deque() for s in self.scenarios}
        self.riders_available = {block: self.demand[block]["riders"] for block in self.demand}
        random.seed(seed)
        self.logger.info("Initialized RealTimeSimulation with scenarios: %s", self.scenarios)

    def get_time_block(self, minute: int):
        # Returns block name for a given minute of the day
        h = (minute // 60) % 24
        m = minute % 60
        t = f"{h:02d}:{m:02d}"
        for block, info in self.demand.items():
            start = info["start"]
            end = info["end"]
            if start < end:
                if start <= t < end:
                    return block
            else:  # overnight
                if t >= start or t < end:
                    return block
        return "night"

    def run(self, verbose=False):
        self.logger.info("Starting real-time simulation for a full day (%d minutes)", self.day_minutes)
        available_riders = {s: {block: self.riders_available[block] for block in self.demand} for s in self.scenarios}
        queues = {s: deque() for s in self.scenarios}
        stats = {s: {"wait_times": [], "serviced": 0, "unsuccessful": 0, "total": 0} for s in self.scenarios}
        trip_probs = {s: {} for s in self.scenarios}
        self.serviced_rides = {s: [] for s in self.scenarios}
        for block, info in self.demand.items():
            for s in self.scenarios:
                trip_probs[s][block] = info[s] / info["minutes"]
        # Simulate each minute for 24 hours (0 to 1439)
        last_logged_second = -1
        for minute in range(self.day_minutes):
            block = self.get_time_block(minute)
            for s in self.scenarios:
                # Generate trip request?
                if random.random() < trip_probs[s][block]:
                    trip = self.city.generate_fatbike_taxi_trip()
                    queues[s].append((minute, trip))
                    stats[s]["total"] += 1
                    self.logger.debug(f"[{s}] Trip requested at min {minute} in block {block}")
                # Try to service queued trips
                riders = available_riders[s][block]
                serviced_now = 0
                new_queue = deque()
                # Only service as many trips as there are available riders, but account for ride duration
                # Track when each rider will be free (list of end times)
                if not hasattr(self, 'rider_busy_until'):
                    self.rider_busy_until = {s: {block: [] for block in self.demand} for s in self.scenarios}
                # Remove riders who are now free
                self.rider_busy_until[s][block] = [t for t in self.rider_busy_until[s][block] if t > minute]
                available_now = riders - len(self.rider_busy_until[s][block])
                while queues[s] and serviced_now < available_now:
                    req_minute, trip = queues[s].popleft()
                    wait = minute - req_minute
                    stats[s]["wait_times"].append(wait)
                    stats[s]["serviced"] += 1
                    serviced_now += 1
                    # Calculate ride duration in minutes
                    ride_duration_min = int(round(trip.get_duration_hours() * 60))
                    self.rider_busy_until[s][block].append(minute + ride_duration_min)
                    # Store ride distance for profit calculation
                    self.serviced_rides[s].append({"distance_km": trip.get_distance_km()})
                    self.logger.debug(f"[{s}] Trip serviced after {wait} min wait at min {minute}, ride duration {ride_duration_min} min")
                    print(f"[SUCCESS] Scenario: {s}, Time: {minute//60:02d}:{minute%60:02d}, Wait: {wait} min, Duration: {ride_duration_min} min, Origin: {trip.origin}, Destination: {trip.destination}")
                # For remaining queued trips, check timeout (now 5 min)
                while queues[s]:
                    req_minute, trip = queues[s].popleft()
                    wait = minute - req_minute
                    if wait >= 5:
                        # Cancel with probability
                        if random.random() < self.cancel_prob:
                            stats[s]["unsuccessful"] += 1
                            self.logger.debug(f"[{s}] Trip cancelled after waiting {wait} min at min {minute}")
                        else:
                            # Still waiting, requeue
                            new_queue.append((req_minute, trip))
                    else:
                        new_queue.append((req_minute, trip))
                queues[s] = new_queue
            # Log timestamp every second (every 60 minutes in simulation)
            if minute % 60 == 0 or minute == self.day_minutes - 1:
                sim_hour = minute // 60
                sim_minute = minute % 60
                self.logger.info(f"Simulated time: {sim_hour:02d}:{sim_minute:02d} (minute {minute})")
            time.sleep(1/60)  # 1 second = 1 hour in simulation (1/60 sec per simulated minute)
        # After last minute, cancel all remaining queued trips
        for s in self.scenarios:
            for req_minute, trip in queues[s]:
                stats[s]["unsuccessful"] += 1
                self.logger.debug(f"[{s}] Trip cancelled at end of day (queued at min {req_minute})")
        self.stats = stats
        self.logger.info("Simulation complete.")
        return stats

    def plot_success_pie(self):
        """
        Plot a pie chart for each scenario showing successful vs unsuccessful rides.
        """
        scenarios = self.scenarios
        fig, axs = plt.subplots(1, len(scenarios), figsize=(6 * len(scenarios), 5))
        if len(scenarios) == 1:
            axs = [axs]
        for idx, s in enumerate(scenarios):
            serviced = self.stats[s]["serviced"]
            unsuccessful = self.stats[s]["unsuccessful"]
            total = serviced + unsuccessful
            axs[idx].pie(
                [serviced, unsuccessful],
                labels=["Successful", "Unsuccessful"],
                autopct=lambda p: f'{int(p * total / 100)} ({p:.1f}%)',
                colors=["#00c49a", "#ff595e"],
                startangle=90,
                explode=(0.05, 0.05),
            )
            axs[idx].set_title(f"{s.title()} Scenario")
        plt.suptitle("Ride Success Rate per Scenario")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def print_results(self):
        total_profit = 0.0
        for s in self.scenarios:
            total = self.stats[s]["total"]
            serviced = self.stats[s]["serviced"]
            unsuccessful = self.stats[s]["unsuccessful"]
            avg_wait = sum(self.stats[s]["wait_times"]) / serviced if serviced > 0 else 0
            # Calculate profit for this scenario
            profit = 0.0
            if hasattr(self, "serviced_rides") and s in self.serviced_rides:
                for ride in self.serviced_rides[s]:
                    ride_profit = 1.5 + 0.2 * ride["distance_km"]
                    profit += ride_profit
            print(f"\nScenario: {s.title()}")
            print(f"  Total trip requests: {total}")
            print(f"  Successful rides: {serviced} ({100*serviced/total:.1f}%)")
            print(f"  Unsuccessful rides: {unsuccessful} ({100*unsuccessful/total:.1f}%)")
            print(f"  Average wait time (min): {avg_wait:.2f}")
            print(f"  Total profit: €{profit:.2f}")
            total_profit += profit
        print(f"\n=== TOTAL PROFIT (all scenarios): €{total_profit:.2f} ===")
        # Plot pie chart for each scenario
        self.plot_success_pie()
