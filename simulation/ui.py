import tkinter as tk
from tkinter import ttk
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from .simulation import Simulation

class UI:
    def __init__(self):
        self.sim = Simulation()
        self.origin = ["Wielewaal", "Barrier", "Muschberg, Geestenberg", "Esp", "Sintenbuurt"]
        self.destination = self.sim.city.zones
        self.weather_types = self.sim.city.weather_types
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(base_dir, "data", "buurten.geojson")
        self.zones_gdf = gpd.read_file(geojson_path)
        self.launch_ui()

    def draw_map(self, selected_zone, ax):
        self.zones_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')
        if selected_zone:
            self.zones_gdf[self.zones_gdf['buurtnaam'] == selected_zone].plot(ax=ax, color='orange', edgecolor='red')

    def update_map(self, selected_var, canvas, ax):
        ax.clear()
        self.draw_map(selected_var.get(), ax)
        canvas.draw()

    def run_simulation(self):
        self.update_values()
        self.sim.set_time_of_day(self.time_of_day)
        print("Running simulation...")
        self.sim.run()

    def update_values(self):
        self.traffic_level = self.traffic_level_slider.get()
        self.time_of_day = self.day_time_slider.get()
        self.start = self.start_var.get()
        self.end = self.end_var.get()
        print(f"Traffic Density: {self.traffic_level}, Time of Day: {self.time_of_day}")
        print(f"Start: {self.start}, End: {self.end}")

    def launch_ui(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Simulation Controls")
        self.container = ttk.Frame(self.root)
        self.container.pack(padx=20, pady=20)
        self.show_tab1()
        self.root.mainloop()

    
    # Tab 1 - Start Point
    def show_tab1(self):
        self.clear_container()

        tk.Label(self.container, text="Start Location").pack(pady=10)
        self.start_var = tk.StringVar()
        
        for zone in self.origin:
            ttk.Radiobutton(self.container, text=zone, variable=self.start_var, value=zone, 
                            command=lambda: self.update_map(self.start_var, self.map_canvas, self.ax)).pack(anchor='w')
            
        # Map canvas
        fig, self.ax = plt.subplots(figsize=(4, 4))
        self.draw_map(self.start_var.get(), self.ax)
        self.map_canvas = FigureCanvasTkAgg(fig, master=self.container)
        self.map_canvas.get_tk_widget().pack(pady=10)


        ttk.Button(self.container, text="Next", command=self.show_tab2).pack(pady=10)

    # Tab 2 - End point dropdown
    def show_tab2(self):
        self.clear_container()

        tk.Label(self.container, text="End Location").pack()
        self.end_var = tk.StringVar()

        for zone in self.destination:
            ttk.Radiobutton(self.container, text=zone, variable=self.end_var, value=zone).pack(anchor='w')

        ttk.Button(self.container, text="Next", command=self.show_tab3).pack(pady=10)

    # Tab 3
    def show_tab3(self):
        self.clear_container()

        # Traffic level slider
        tk.Label(self.container, text="Traffic Density").pack()
        self.traffic_level_slider = tk.Scale(self.container, from_=0, to=100, orient="horizontal")
        self.traffic_level_slider.pack()
        # Time
        tk.Label(self.container, text="Time of Day").pack()
        self.day_time_slider = tk.Scale(self.container, from_=0, to=23, orient="horizontal")
        self.day_time_slider.pack()
        # Weather
        tk.Label(self.container, text="Weather").pack()
        self.weather_var = tk.StringVar(value=self.weather_types[0])

        for weather in self.weather_types:
            ttk.Radiobutton(self.container, text=weather, variable=self.weather_var, value=weather).pack(anchor='w')

        # Submit button
        tk.Button(self.container, text="Start Simulation", command=self.run_simulation).pack(pady=10)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
