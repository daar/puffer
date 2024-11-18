"""
Module for managing the extrusion calibration tab in a Tkinter application.

This module defines the `ExtrusionCalibrationTab` class, which extends the `BaseTab` class.
It provides a user interface for calibrating the extruder's steps-per-millimeter by measuring
filament usage, adjusting the extrusion factor, and monitoring the hotend temperature.
"""

from tkinter import ttk, messagebox
import time
from ui.base_tab import BaseTab
from utils.gcode_utils import send_gcode, parse_gcode_response


class ExtrusionCalibrationTab(BaseTab):
    """
    A class representing the extrusion calibration tab in a Tkinter notebook.

    This tab allows users to calibrate the extruder by measuring the initial and
    remaining filament lengths, extruding a specific amount, and adjusting the steps
    per millimeter. It also monitors and updates the hotend temperature.

    Attributes:
        initial_length (ttk.Entry): Entry widget for the initial filament length.
        remaining_filament (ttk.Entry): Entry widget for the remaining filament length.
        extrude_button (ttk.Button): Button to extrude the specified filament length.
        adjust_button (ttk.Button): Button to adjust the extrusion factor.
        output_area (ttk.Label): Label to display operation results.
        temperature_label (ttk.Label): Label to display the current hotend temperature.
    """

    def __init__(self, tabs, app, tab_name):
        """
        Initialize the ExtrusionCalibrationTab instance.

        Args:
            tabs (ttk.Notebook): The notebook widget to which this tab is added.
            app (Any): The main application instance providing the printer connection and utilities.
            tab_name (str): The name to display on this tab.
        """
        super().__init__(tabs, app, tab_name)
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface for the extrusion calibration tab.
        """
        frame = ttk.Frame(self.frame, padding=10)
        frame.pack(fill="x")

        # Inputs
        ttk.Label(frame, text="Initial Filament Length (mm):").grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.initial_length = ttk.Entry(frame, width=10)
        self.initial_length.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Remaining Filament Length (mm):").grid(
            row=1, column=0, sticky="w", padx=5
        )
        self.remaining_filament = ttk.Entry(frame, width=10)
        self.remaining_filament.grid(row=1, column=1, padx=5)

        self.extrude_button = ttk.Button(
            frame, text="Extrude", command=self.extrude_length
        )
        self.extrude_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.adjust_button = ttk.Button(
            frame, text="Adjust Extrusion", command=self.adjust_extrusion_factor
        )
        self.adjust_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Output area
        self.output_area = ttk.Label(
            self.frame, text="Results will appear here", anchor="w"
        )
        self.output_area.pack(fill="x", padx=10, pady=5)

        # Live temperature display
        self.temperature_label = ttk.Label(
            self.frame, text="Hotend Temp: Waiting for data..."
        )
        self.temperature_label.pack(pady=10, padx=10)

        # Start the temperature update loop
        self.update_temperature()

    def update_temperature(self):
        """
        Update the hotend temperature every second.
        """
        current_temp = self.check_hotend_temperature()
        if current_temp is not None:
            self.temperature_label.config(text=f"Hotend Temp: {current_temp}°C")
        else:
            self.temperature_label.config(
                text="Hotend Temp: Error reading temperature."
            )

        # Call this function again after 1000ms (1 second)
        self.frame.after(1000, self.update_temperature)

    def check_hotend_temperature(self):
        """
        Check the current hotend temperature.
        """
        return self.send_and_receive_gcode("M105", "T:")

    def extrude_length(self):
        """
        Extrude the length of filament and measure the remaining filament.
        """
        try:
            if not self.check_printer_connection():
                return

            initial_length = float(self.initial_length.get())
            remaining_filament = float(self.remaining_filament.get())

            # Calculate how much to extrude based on the difference between the
            # initial and remaining filament
            length_to_extrude = initial_length - remaining_filament

            if length_to_extrude < 10:  # Ensuring a minimum of 10mm to extrude
                raise ValueError("You must extrude at least 10mm.")

            # Check if the hotend is at 210°C
            current_temp = self.check_hotend_temperature()
            if current_temp is None:
                raise ValueError("Failed to read hotend temperature.")
            if current_temp < 210:
                # If the hotend temperature is less than 210°C, heat it
                self.heat_hotend()

            # Send M302 to allow extrusion regardless of temperature
            send_gcode(
                self.app.serial_connection, "M302", self.app.append_message
            )  # Enable extrusion regardless of temperature

            # Move the extruder to start the extrusion
            # Move the extruder by a small amount to ensure it’s primed
            send_gcode(
                self.app.serial_connection, "G1 E5 F300", self.app.append_message
            )  # Move extruder by 5mm to prime it

            # Now extrude the required amount
            send_gcode(
                self.app.serial_connection,
                f"G1 E{length_to_extrude} F300",
                self.app.append_message,
            )
            self.output_area.config(
                text=f"Extruded {length_to_extrude}mm. Measure remaining filament length."
            )

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def heat_hotend(self):
        """
        Heat the hotend to 210°C if the temperature is below 210°C.
        """
        self.set_status_message("Heating hotend to 210°C...", error=True)
        send_gcode(
            self.app.serial_connection, "M104 S210", self.app.append_message
        )  # Set hotend to 210°C
        while True:
            time.sleep(1)  # Wait for a second
            current_temp = self.check_hotend_temperature()
            if current_temp is not None and current_temp >= 210:
                break
        self.set_status_message("Hotend reached 210°C.")

    def adjust_extrusion_factor(self):
        """
        Adjust the extruder steps based on the measured extrusion.
        """
        initial_length = float(self.initial_length.get())
        remaining_length = float(self.remaining_filament.get())
        actual_extruded = initial_length - remaining_length

        if actual_extruded <= 0:
            raise ValueError("Invalid extrusion measurement.")

        adjustment_factor = 100 / actual_extruded
        current_steps = self.get_current_extruder_steps()
        new_steps = current_steps * adjustment_factor

        send_gcode(
            self.app.serial_connection,
            f"M92 E{new_steps:.2f}",
            self.app.append_message,
        )
        send_gcode(self.app.serial_connection, "M500", self.app.append_message)

        self.output_area.config(
            text=f"Extrusion adjusted. New steps/mm: {new_steps:.2f}"
        )

    def get_current_extruder_steps(self):
        """
        Get the current extruder steps from the printer by sending M503.
        """
        send_gcode(self.app.serial_connection, "M503", self.app.append_message)
        response = parse_gcode_response(self.app.serial_connection)
        for line in response:
            if "M92" in line:
                return float(line.split("E")[1])
        raise ValueError("Failed to read current extruder steps.")
