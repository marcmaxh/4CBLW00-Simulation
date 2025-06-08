from simulation.ui import UI
from simulation.simulation import Simulation
from utils import plotting

if __name__ == "__main__":
    ui = UI()

if __name__ == "__main__":
    sim = Simulation(num_trips=10000, use_real_data=False)
    sim.set_time_of_day("rush_hour")
    results = sim.run()
    print("\n--- CO2 savings for different modal shift scenarios ---")
    for shift in [0.516, 0.31, 0.155]:
        sim.summarize_results(results, car_shift=shift)
    summary = plotting.summarize_for_plot(results)
    plotting.plot_summary(summary)
    plotting.plot_distributions_per_vehicle(results)
