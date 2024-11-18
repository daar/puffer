import tkinter as tk
from tkinter import ttk, messagebox
import time
import serial
from ui.base_tab import BaseTab


class ConnectionTab(BaseTab):
    def __init__(self, tabs, app, tab_name):
        super().__init__(tabs, app, tab_name)
        self.auto_home = tk.BooleanVar(value=False)  # Checkbox state
        self.setup_ui()

    def setup_ui(self):
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
        """Attempt to connect to the printer."""
        try:
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
                except serial.SerialException as e:
                    continue  # Try the next port if the current one fails

            else:
                # If no connection was successful, show an error
                messagebox.showerror("Error", "Failed to connect to any printer port.")

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")

    def perform_auto_homing(self):
        """Send G-code for auto-homing."""
        try:
            self.app.append_message("Sending auto-home command (G28)...")
            if self.app.serial_connection:
                self.app.serial_connection.write(
                    "G28\n".encode()
                )  # Send G-code to auto-home the printer
                self.app.append_message("Auto-home command sent.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to perform auto-homing: {e}")

    def refresh_treeview(self):
        """Populate the treeview with real printer data."""
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
