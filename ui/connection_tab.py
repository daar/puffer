"""
Module for managing the connection tab in a Tkinter application.

This module defines the `ConnectionTab` class, which extends the `BaseTab` class
to provide a user interface for connecting to a 3D printer. It includes functionality
for managing connection settings, auto-homing, and displaying printer data.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import serial
from ui.base_tab import BaseTab


class ConnectionTab(BaseTab):
    """
    A class representing the connection tab in a Tkinter notebook.

    This tab allows users to connect to a 3D printer, send auto-homing commands,
    and view printer data such as firmware information and settings.

    Attributes:
        auto_home (tk.BooleanVar): A variable for managing the state of the
                                   auto-home checkbox.
        connection_status (ttk.Label): A label displaying the current connection status.
        connect_button (ttk.Button): A button to initiate connection to the printer.
        auto_home_checkbox (ttk.Checkbutton): A checkbox for enabling/disabling
                                              auto-home on connection.
        refresh_button (ttk.Button): A button to refresh the printer data.
        treeview (ttk.Treeview): A treeview widget to display printer data.
    """

    def __init__(self, tabs, app, tab_name):
        """
        Initialize the ConnectionTab instance.

        Args:
            tabs (ttk.Notebook): The notebook widget to which this tab is added.
            app (Any): The main application instance providing the printer
                       connection and related utilities.
            tab_name (str): The name to display on this tab.
        """
        super().__init__(tabs, app, tab_name)
        self.auto_home = tk.BooleanVar(value=False)  # Checkbox state
        self.setup_ui()

    def setup_ui(self):
        """
        Set up the user interface for the connection tab.

        This method creates and arranges widgets, including labels, buttons,
        checkboxes, and a treeview for displaying printer data.
        """
        # Connection controls
        frame = ttk.Frame(self.frame, padding=10)
        frame.pack(fill="x")

        # Connection Status Label
        ttk.Label(frame, text="Connection Status:").grid(row=0, column=0, sticky="w")
        self.connection_status = ttk.Label(frame, text="Not Connected")
        self.connection_status.grid(row=0, column=1, sticky="w")

        # Connect Button
        self.connect_button = ttk.Button(
            frame, text="Connect", command=self.connect_to_printer
        )
        self.connect_button.grid(row=0, column=2, padx=5)

        # Auto-Home Checkbox
        self.auto_home_checkbox = ttk.Checkbutton(
            frame, text="Auto-home on connect", variable=self.auto_home
        )
        self.auto_home_checkbox.grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        # Refresh Button
        self.refresh_button = ttk.Button(
            frame, text="Refresh", command=self.refresh_treeview, state=tk.DISABLED
        )
        self.refresh_button.grid(row=1, column=2, padx=5)

        # Treeview for printer data
        self.treeview = ttk.Treeview(
            self.frame, columns=("Key", "Value"), show="tree headings"
        )
        self.treeview.heading("Key", text="Key")
        self.treeview.heading("Value", text="Value")
        self.treeview.column("#0", width=150, anchor="w")  # Parent nodes
        self.treeview.column("Key", width=200, anchor="w")
        self.treeview.column("Value", width=400, anchor="w")
        self.treeview.pack(fill="both", expand=1, padx=10, pady=10)

    def connect_to_printer(self):
        """
        Attempt to connect to the printer.

        This method scans for available serial ports and tries to establish
        a connection. If successful, it updates the connection status and
        optionally performs auto-homing.
        """
        ports = self.app.list_serial_ports()
        if not ports:
            messagebox.showerror(
                "Error", "No serial ports found. Please connect your printer."
            )
            return

        for port in ports:
            try:
                print(f"Attempting to connect to {port}...")
                self.app.serial_connection = serial.Serial(port, 115200, timeout=2)
                self.connection_status.config(text="Connected")
                self.app.append_message(f"Printer connected on {port}.")

                # Perform auto-homing if the checkbox is selected
                if self.auto_home.get():
                    self.perform_auto_homing()

                # Enable the refresh button after connection
                self.refresh_button.config(state=tk.NORMAL)

                # Refresh treeview data
                self.refresh_treeview()
                break  # Exit the loop once a connection is successful
            except serial.SerialException:
                continue  # Try the next port if the current one fails

        else:
            # If no connection was successful, show an error
            messagebox.showerror("Error", "Failed to connect to any printer port.")

    def perform_auto_homing(self):
        """
        Send the G-code command to auto-home the printer.

        This method sends the G28 command to the printer if a serial connection
        is active.
        """
        self.app.append_message("Sending auto-home command (G28)...")
        if self.app.serial_connection:
            self.app.serial_connection.write(
                "G28\n".encode()
            )  # Send G-code to auto-home the printer
            self.app.append_message("Auto-home command sent.")

    def refresh_treeview(self):
        """
        Populate the treeview widget with data from the printer.

        This method sends various G-code commands to the printer and displays
        the parsed responses in the treeview. Each G-code command creates a
        parent node, and its data is added as child nodes.
        """
        if not self.app.serial_connection:
            messagebox.showerror("Error", "Not connected to a printer.")
            return

        # Clear the current treeview content
        self.treeview.delete(*self.treeview.get_children())

        # Send necessary G-code commands to get printer settings
        gcodes = {
            "Firmware Info": "M115",  # Get firmware information
            "Current Settings": "M503",  # Get current printer settings
            "Position": "M114",  # Get current position
            "Endstop Status": "M119",  # Endstop status
        }

        # Loop through each G-code command, send it, and parse the response
        for key, gcode in gcodes.items():
            self.app.serial_connection.write(
                f"{gcode}\n".encode()
            )  # Send the G-code command
            time.sleep(0.5)  # Wait for the printer to respond
            response = self.app.read_response()  # Read the response from the printer

            # Add parent node for the G-code command
            parent_id = self.treeview.insert("", tk.END, text=key, values=("", ""))

            # Parse the response and add child nodes
            for line in response:
                if ":" in line:
                    k, v = map(str.strip, line.split(":", 1))
                    self.treeview.insert(parent_id, tk.END, text="", values=(k, v))
                elif "=" in line:
                    k, v = map(str.strip, line.split("=", 1))
                    self.treeview.insert(parent_id, tk.END, text="", values=(k, v))
                else:
                    self.treeview.insert(parent_id, tk.END, text="", values=(line, ""))

        self.app.append_message("Data refreshed successfully.")
