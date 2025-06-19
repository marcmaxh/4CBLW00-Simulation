import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
from PIL import Image, ImageTk
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

    def apply_style(self):
        self.bg_color = "#F0FFFF"
        self.fg_color = "#7393B3"
        self.accent_color = "#87CEFA"
        self.font = ("Arial", 12)

        style = ttk.Style()
        style.theme_use("clam")

        # Background
        style.configure(".", background=self.bg_color, foreground=self.fg_color, font=self.font)
        style.configure("TButton", background=self.accent_color, foreground=self.fg_color)
        style.map("TButton", background=[("active", "#3B82F6")])
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TRadiobutton", background=self.bg_color, foreground=self.fg_color)

        self.root.configure(bg=self.bg_color)
        self.container.configure(style="TFrame")

    def draw_map(self, selected_zone, ax, dest=None):
        self.zones_gdf.plot(ax=ax, color=self.bg_color, edgecolor='black')
        for zone in self.origin:
            self.zones_gdf[self.zones_gdf['buurtnaam'] == zone].plot(ax=ax, color=self.fg_color, edgecolor='black')
        if selected_zone:
            self.zones_gdf[self.zones_gdf['buurtnaam'] == selected_zone].plot(ax=ax, color=self.accent_color, edgecolor='black')
        if dest != None:
            dx, dy = self.dest_coords[dest]
            ax.scatter(dx, dy, color='black', marker='x', s=80, label="Destinations")


    def update_map(self, selected_var, canvas, ax):
        self.update_values()
        ax.clear()
        self.draw_map(selected_var.get(), ax)
        canvas.draw()
    
    def update_odmap(self, dest):
        if not hasattr(self, 'ax_tab2'):
            return
            
        self.ax_tab2.clear()

        # Calculate aspect ratio again to maintain it
        bounds = self.zones_gdf.total_bounds
        x_range = bounds[2] - bounds[0]
        y_range = bounds[3] - bounds[1]
        aspect_ratio = y_range / x_range
        self.ax_tab2.set_aspect(aspect_ratio)
        
        # Plot all zones
        self.zones_gdf.plot(ax=self.ax_tab2, color='azure', edgecolor='black', alpha=0.5)
        
        # Highlight origin
        origin = self.start_var.get()
        if origin:
            self.zones_gdf[self.zones_gdf['buurtnaam'] == origin].plot(
                ax=self.ax_tab2, color=self.accent_color, edgecolor='black', alpha=0.7
            )
        
        # Plot destination marker
        if dest and dest in self.dest_coords:
            coords = self.dest_coords[dest]
            self.ax_tab2.scatter(
                coords['longitude'], 
                coords['latitude'], 
                color='orange', 
                s=80,
                marker='X',
                edgecolor='black',
                label=dest
            )
        
        # Set title and legend
        self.ax_tab2.set_title(f"Origin: {origin}\nDestination: {dest if dest else 'Not selected'}", color=self.fg_color)

        self.ax_tab2.set_facecolor(self.bg_color)
        self.canvas_tab2.draw()

    def show_summary_plot(self, results):
        summary = plotting.summarize_for_plot(results)
        fig1 = plotting.plot_summary(summary)
        fig2 = plotting.plot_distributions_per_vehicle(results)

        # Create a new Toplevel window
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Simulation Plots")

        # Create a Notebook (tabbed interface) to switch between plots
        notebook = ttk.Notebook(plot_window)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Summary plot
        frame1 = ttk.Frame(notebook)
        notebook.add(frame1, text="Summary")
        canvas1 = FigureCanvasTkAgg(fig1, master=frame1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 2: Distributions plot
        frame2 = ttk.Frame(notebook)
        notebook.add(frame2, text="Distributions")
        canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add close button in the new window
        button_frame = ttk.Frame(plot_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Close", command=plot_window.destroy).pack()

        # Control window still shows Restart and Back
        self.clear_container()
        ttk.Label(self.container, text="Simulation Completed", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self.container, text="Thank you for using VeloCity", font=("Arial", 14)).pack(pady=10)
        ttk.Label(self.container, textvariable=self.status_var).pack(pady=5)
        ttk.Button(self.container, text="Back", command=self.show_tab3).pack(side="left", padx=10)
        ttk.Button(self.container, text="Restart", command=self.show_tab1).pack(side="right", padx=10)
        
    def update_values(self):
        self.start = self.start_var.get() if hasattr(self, 'start_var') else ''
        self.end = self.end_var.get() if hasattr(self, 'end_var') else ''
        self.tod = self.time_var.get() if hasattr(self, 'time_var') else ''
        self.weather = self.weather_var.get() if hasattr(self, 'weather_var') else ''
        self.status_var.set(f"Origin: {self.start}, Destination: {self.end}, Time: {self.tod}, Weather: {self.weather}")

    def launch_ui(self):
        csv_path = os.path.join(self.base_dir, "simulation", "Origin to POI.csv")
        self.od_map = self.load_csv(csv_path)
        json_path = os.path.join(self.base_dir, "data", "destination_coordinates.json")
        with open(json_path, 'r', encoding='utf-8') as file:
            self.dest_coords = json.load(file)
        self.origin = sorted(self.od_map.keys())
        self.origin.remove('\ufeffOrigin')
    
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Simulation Controls")
        self.container = ttk.Frame(self.root)
        self.container.pack(padx=20, pady=20)
        self.status_var = tk.StringVar()
        self.apply_style()
        logo_path = os.path.join(self.base_dir, "image", "Logo.png")
        img = Image.open(logo_path)
        width, height = img.size
        left = 0.06 * width
        right = 0.95 * width
        top = 0.3 * height
        bottom = 0.7 * height
        cropped_img = img.crop((left, top, right, bottom))
        width, height = cropped_img.size
        logo_large = cropped_img.resize((int(0.3 * width), int(0.3 * height)))
        logo_img = cropped_img.resize((int(0.08 * width), int(0.08 * height)))
        self.logo_photo = ImageTk.PhotoImage(logo_img)
        self.logo_cover = ImageTk.PhotoImage(logo_large)
        self.show_tab0()
        self.root.mainloop()

    # Tab 1 - Start Point
    def show_tab0(self):
        self.clear_container()
        # Create main container frame
        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for logo (and optionally a title)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Add logo
        logo_label = ttk.Label(top_frame, image=self.logo_cover)
        logo_label.image = self.logo_cover
        logo_label.pack()
        ttk.Label(self.container, text="Welcome to VeloCity", font=("Arial", 20)).pack(pady=(5, 10))
        ttk.Label(self.container, text="To start, please press the button", font=("Arial", 12)).pack(pady=(5, 10))
        ttk.Button(self.container, text="Start Model", command=self.show_tab1).pack(pady=10)


    # Tab 1 - Start Point
    def show_tab1(self):
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.weather_var = tk.StringVar()
        self.update_values()
        self.clear_container()
        
        # Create main container frame
        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for logo (and optionally a title)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Add logo
        logo_label = ttk.Label(top_frame, image=self.logo_photo)
        logo_label.image = self.logo_photo
        logo_label.pack()
        def check_ready_and_proceed():
            if not self.start_var.get():
                messagebox.showwarning("Missing Info", "Please select a destination.")
            else:
                self.show_tab2()

        ttk.Label(self.container, text="Start Location", style="TLabel").pack(pady=10)
        
        for zone in self.origin:
            ttk.Radiobutton(self.container, text=zone, variable=self.start_var, value=zone, 
                            command=lambda: self.update_map(self.start_var, self.map_canvas, self.ax)).pack(anchor='w')
            
        # Map canvas
        fig, self.ax = plt.subplots(figsize=(4, 4))
        fig.patch.set_facecolor(self.bg_color)
        self.ax.set_facecolor(self.bg_color)
        self.draw_map(self.start_var.get(), self.ax)
        self.map_canvas = FigureCanvasTkAgg(fig, master=self.container)
        self.map_canvas.get_tk_widget().pack(pady=10)

        ttk.Label(self.container, textvariable=self.status_var, style="TLabel").pack(pady=5)

        ttk.Button(self.container, text="Next", command=check_ready_and_proceed).pack(pady=10)

    # Tab 2 - End point dropdown
    def show_tab2(self):
        self.end_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.weather_var = tk.StringVar()
        self.update_values()
        
        def check_ready_and_proceed():
            if not self.end_var.get():
                messagebox.showwarning("Missing Info", "Please select a destination.")
            else:
                self.show_tab3()

        self.clear_container()

                # Create main container frame
        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for logo (and optionally a title)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Add logo
        logo_label = ttk.Label(top_frame, image=self.logo_photo)
        logo_label.image = self.logo_photo
        logo_label.pack()

        self.dest_img_refs = []

        selected_origin = self.start_var.get()
        valid_destinations = sorted(self.od_map.get(selected_origin, []))

        # Create main container frame
        main_frame = ttk.Frame(self.container, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for destination selection
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        ttk.Label(left_frame, text="End Location", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        # Create canvas for scrolling
        canvas = tk.Canvas(left_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for dest in valid_destinations:
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill='x', pady=4, padx=5)
            frame.configure(bg=self.bg_color)

            # Load image
            img_path = os.path.join(self.base_dir, "image", f"{dest.replace('/', '(').replace('_', ' ')}.jpg")
            img = None
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path).resize((64, 64))
                    photo = ImageTk.PhotoImage(img)
                    img_label = ttk.Label(frame, image=photo)
                    img_label.image = photo
                    img_label.pack(side='left', padx=(0, 10))
                    self.dest_img_refs.append(photo)
                except Exception as e:
                    print(f"Error loading image {img_path}: {str(e)}")

            # Destination name formatting
            dest_name = dest.replace("_", " ").title()

            # Radio button with image on the left
            radio_btn = ttk.Radiobutton(frame, text=dest_name, variable=self.end_var, value=dest,
                                        command=lambda d=dest: self.update_odmap(d))
            radio_btn.pack(side='left')

        # Right frame for map
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create map
        fig = Figure(figsize=(4, 4))
        fig.patch.set_facecolor(self.bg_color)
        self.ax.set_facecolor(self.bg_color)
        self.ax_tab2 = fig.add_subplot(111)

        # Calculate proper aspect ratio based on coordinates
        bounds = self.zones_gdf.total_bounds
        x_range = bounds[2] - bounds[0]
        y_range = bounds[3] - bounds[1]
        aspect_ratio = y_range / x_range
        
        # Set the correct aspect ratio
        self.ax_tab2.set_aspect(aspect_ratio)
        
        self.canvas_tab2 = FigureCanvasTkAgg(fig, master=right_frame)
        self.canvas_tab2.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Draw initial map
        self.update_odmap(None)


        # label
        ttk.Label(self.container, textvariable=self.status_var).pack(pady=5)
        btn_frame = tk.Frame(self.container)
        btn_frame.pack(pady=10, fill='x')
        ttk.Button(self.container, text="Back", command=self.show_tab1).pack(side="left", padx=10, pady=10)
        ttk.Button(self.container, text="Next", command=check_ready_and_proceed).pack(side="right", padx=10, pady=10)

    # Tab 3
    def show_tab3(self):
        self.time_var = tk.StringVar()
        self.weather_var = tk.StringVar()
        self.update_values()
        self.clear_container()

        # Create main container frame
        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for logo (and optionally a title)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Add logo
        logo_label = ttk.Label(top_frame, image=self.logo_photo)
        logo_label.image = self.logo_photo
        logo_label.pack()

        def check_ready_and_proceed():
            if not self.time_var.get():
                messagebox.showwarning("Missing Info", "Please select a time.")
            elif not self.weather_var.get():
                messagebox.showwarning("Missing Info", "Please select the weather.")
            else:
                self.show_tab4()

        # Time
        ttk.Label(self.container, text="Time of the day", font=("Arial", 14, "bold")).pack(pady=(10, 5))

        for time in self.time_of_day:
            display_time = time.replace("_", " ").title()
            ttk.Radiobutton(self.container, text=display_time, variable=self.time_var, value=time, 
                            command=self.update_values).pack(anchor='w')

        # Weather
        ttk.Label(self.container, text="Weather", font=("Arial", 14, "bold")).pack(pady=(15, 5))

        for weather in self.weather_types:
            ttk.Radiobutton(self.container, text=weather.title(), variable=self.weather_var, value=weather, 
                            command=self.update_values).pack(anchor='w')


        ttk.Label(self.container, textvariable=self.status_var).pack(pady=5)
        
        # Submit button
        ttk.Button(self.container, text="Back", command=self.show_tab2).pack(side="left", padx=10, pady=10)
        ttk.Button(self.container, text="Start Simulation", command=check_ready_and_proceed).pack(side = "right", padx=10, pady=10)

    # Tab 4
    def show_tab4(self):
        self.update_values()
        self.clear_container()

        # Create main container frame
        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for logo (and optionally a title)
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Add logo
        logo_label = ttk.Label(top_frame, image=self.logo_photo)
        logo_label.image = self.logo_photo
        logo_label.pack()

        # Indicate simulation is running
        loading_label = ttk.Label(self.container, text="Running simulation...", font=("Arial", 12, "italic"))
        loading_label.pack(pady=20)
        self.root.update_idletasks()  # Force UI update

        # Run the simulation
        self.sim.set_time_of_day(self.tod)
        result = self.sim.run_for_od_pair(self.start, self.end)

        # Remove loading label
        loading_label.destroy()

        # Show the plots
        self.show_summary_plot(result)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.container.configure(style="TFrame")
