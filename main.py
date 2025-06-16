from simulation.ui import UI
from simulation.simulation import Simulation
from simulation.real_time_simulation import RealTimeSimulation
from utils import plotting
import argparse

# Run with python main.py n for n in {1, 2, 3} to execute the desired option

# Option 1: Run the UI
def run_option_1():
    ui = UI()

# Option 2: Run the standard simulation
def run_option_2():
    sim = Simulation(num_trips=10000, use_real_data=False)
    sim.set_time_of_day("rush_hour")
    results = sim.run()
    print("\n--- CO2 savings for different modal shift scenarios ---")
    for shift in [0.516, 0.31, 0.155]:
        sim.summarize_results(results, car_shift=shift)
    summary = plotting.summarize_for_plot(results)
    plotting.plot_summary(summary)
    plotting.plot_distributions_per_vehicle(results)

#  Option 3: Run the real-time simulation
def run_option_3():
    print("\n--- Running Real-Time Simulation ---")
    rt_sim = RealTimeSimulation()
    rt_sim.run(verbose=False)
    rt_sim.print_results()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run different simulation options.")
    parser.add_argument("option", type=int, choices=[1, 2, 3], 
                       help="Option to run: 1 for UI, 2 for standard simulation, 3 for real-time simulation")

    # Parse arguments
    args = parser.parse_args()

    # Run the selected option
    if args.option == 1:
        run_option_1()
    elif args.option == 2:
        run_option_2()
    elif args.option == 3:
        run_option_3()
    else:
        print("Invalid")

if __name__ == "__main__":
    main()
