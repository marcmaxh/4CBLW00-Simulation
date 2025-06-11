import tkinter as tk
from tkinter import ttk
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
import os

from .simulation import Simulation
from utils import plotting

class UI:
    def __init__(self):
        self.sim = Simulation()
        self.time_of_day = ["night", "off_peak", "midday", "rush_hour"]
        # self.origin = ["Wielewaal", "Barrier", "Muschberg, Geestenberg", "Esp", "Sintenbuurt"]
        # self.destination = self.sim.city.zones
        self.weather_types = self.sim.city.weather_types
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        geojson_path = os.path.join(self.base_dir, "data", "buurten.geojson")
        self.zones_gdf = gpd.read_file(geojson_path)
        self.launch_ui()

    def load_csv(self, csv_path):
        od_map = {}
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row or not row[0].strip() or not row[1].strip():
                    continue
                origin = row[0].strip()
                destination = row[1].strip()
                if origin not in od_map:
                    od_map[origin] = set()
                od_map[origin].add(destination)
        return od_map

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
        self.sim.set_time_of_day(self.tod)
        result = self.sim.run_for_od_pair(self.start, self.end)
        self.show_summary_plot(result)


    def show_summary_plot(self, results):
        summary = plotting.summarize_for_plot(results)
        fig = plotting.plot_summary(summary)

        # Clear container
        self.clear_container()

        # Embed plot
        canvas = FigureCanvasTkAgg(fig, master=self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Back button
        tk.Button(self.container, text="Back", command=self.show_tab3).pack(pady=10)

    def update_values(self):
        self.tod = self.time_var.get()
        self.start = self.start_var.get()
        self.end = self.end_var.get()
        print("Time of Day: {self.tod}")
        print(f"Start: {self.start}, End: {self.end}")

    def launch_ui(self):
        csv_path = os.path.join(self.base_dir, "simulation", "Origin to POI.csv")
        self.od_map = self.load_csv(csv_path)
        self.origin = sorted(self.od_map.keys())
    
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

        selected_origin = self.start_var.get()
        valid_destinations = sorted(self.od_map.get(selected_origin, []))

        tk.Label(self.container, text="End Location").pack()
        self.end_var = tk.StringVar()

        for zone in valid_destinations:
            ttk.Radiobutton(self.container, text=zone, variable=self.end_var, value=zone).pack(anchor='w')

        ttk.Button(self.container, text="Back", command=self.show_tab1).pack(side="left", padx=10, pady=10)
        ttk.Button(self.container, text="Next", command=self.show_tab3).pack(side="right", padx=10, pady=10)

    # Tab 3
    def show_tab3(self):
        self.clear_container()

        # Time
        tk.Label(self.container, text="Time of the day", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.time_var = tk.StringVar(value=self.time_of_day[3])

        for time in self.time_of_day:
            display_time = time.replace("_", " ").title()
            ttk.Radiobutton(self.container, text=display_time, variable=self.time_var, value=time).pack(anchor='w')

        # Weather
        tk.Label(self.container, text="Weather", font=("Arial", 14, "bold")).pack(pady=(15, 5))
        self.weather_var = tk.StringVar(value=self.weather_types[0])

        for weather in self.weather_types:
            ttk.Radiobutton(self.container, text=weather.title(), variable=self.weather_var, value=weather).pack(anchor='w')


        # Submit button
        ttk.Button(self.container, text="Back", command=self.show_tab2).pack(side="left", padx=10, pady=10)
        tk.Button(self.container, text="Start Simulation", command=self.run_simulation).pack(side = "right", padx=10, pady=10)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
