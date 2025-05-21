import tkinter as tk
from tkinter import ttk

def launch_ui():
    def update_values():
        traffic_level = traffic_level_slider.get()
        day_time = day_time_slider.get()
        start = start_var.get()
        end = end_var.get()
        print(f"Traffic Density: {traffic_level}, Day Time: {day_time}")
        print(f"Start: {start}, End: {end}")

    origin = ["1", "2", "3"]

    # Sample location options
    destination = ["Station", "City Center", "University", "Airport", "Shop"]

    # Create the main window
    root = tk.Tk()
    root.title("Simulation Controls")

    # Traffic level slider
    tk.Label(root, text="Traffic Density").pack()
    traffic_level_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
    traffic_level_slider.pack()

    # Weather slider
    tk.Label(root, text="Day Time").pack()
    day_time_slider = tk.Scale(root, from_=0, to=23, orient="horizontal")
    day_time_slider.pack()

    # Start point dropdown
    tk.Label(root, text="Start Location").pack()
    start_var = tk.StringVar()
    start_dropdown = ttk.Combobox(root, textvariable=start_var, values=origin)
    start_dropdown.pack()
    start_dropdown.current(0)

    # End point dropdown
    tk.Label(root, text="End Location").pack()
    end_var = tk.StringVar()
    end_dropdown = ttk.Combobox(root, textvariable=end_var, values=destination)
    end_dropdown.pack()
    end_dropdown.current(1)

    # Submit button
    tk.Button(root, text="Run Simulation", command=update_values).pack()

    root.mainloop()