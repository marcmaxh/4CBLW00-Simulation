import tkinter as tk
from tkinter import ttk
from .simulation import Simulation

class UI:
    def __init__(self):
        self.sim = Simulation()
        self.root = tk.Tk()
        self.root.title("Simulation Controls")
        self.launch_ui()

    def run_simulation(self):
        self.update_values()
        self.sim.set_time_of_day(self.time_of_day)
        print("Running simulation...")
        self.sim.run()

    def update_values(self):
        self.traffic_level = self.traffic_level_slider.get()
        self.time_of_day = self.day_time_slider.get()
        self.start = self.start_dropdown.get()
        self.end = self.end_dropdown.get()
        print(f"Traffic Density: {self.traffic_level}, Time of Day: {self.time_of_day}")
        print(f"Start: {self.start}, End: {self.end}")

    def launch_ui(self):

        origin = self.sim.city.zones


        # Sample location options
        destination = self.sim.city.zones

        # Create the main window
        root = tk.Tk()
        root.title("Simulation Controls")

        # Traffic level slider
        tk.Label(root, text="Traffic Density").pack()
        self.traffic_level_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
        self.traffic_level_slider.pack()

        # Time
        tk.Label(root, text="Time of Day").pack()
        self.day_time_slider = tk.Scale(root, from_=0, to=23, orient="horizontal")
        self.day_time_slider.pack()

        # Start point dropdown
        tk.Label(root, text="Start Location").pack()
        self.start_var = tk.StringVar()
        self.start_dropdown = ttk.Combobox(root, textvariable=self.start_var, values=origin)
        self.start_dropdown.pack()
        self.start_dropdown.current(0)

        # End point dropdown
        tk.Label(root, text="End Location").pack()
        self.end_var = tk.StringVar()
        self.end_dropdown = ttk.Combobox(root, textvariable=self.end_var, values=destination)
        self.end_dropdown.pack()
        self.end_dropdown.current(1)

        # Submit button
        tk.Button(root, text="Start Simulation", command=self.run_simulation).pack(pady=10)

        root.mainloop()