"""
A GUI application for controlling a 3D printer using serial communication.

This module provides a Tkinter-based interface for managing printer settings,
sending G-code commands, and monitoring printer responses. It includes features
such as tab management for different functionalities, a serial connection for
communication, and a message log for tracking user actions and printer responses.
"""

import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import serial
from ui.tab_manager import setup_tabs


class PrinterControlApp:
    """
    The main application class for the 3D Printer Control interface.

    This class initializes the Tkinter GUI, manages the serial connection to the
    printer, and provides methods for logging messages and handling serial communication.

    Attributes:
        root (tk.Tk): The root window of the Tkinter application.
        serial_connection (serial.Serial): The serial connection to the printer.
        message_log (list of str): A list to store logged messages.
        tabs (ttk.Notebook): The notebook widget managing application tabs.
        message_frame (ttk.Frame): A frame containing the message log at the bottom.
        message_listbox (tk.Listbox): A listbox widget to display logged messages.
    """

    def __init__(self, root):
        """
        Initialize the PrinterControlApp with the given Tkinter root window.

        Args:
            root (tk.Tk): The root window of the application.
        """
        self.root = root
        self.serial_connection = None
        self.message_log = []

        # Set up the main menu
        self.setup_main_menu()

        # Set up the tab interface
        self.tabs = ttk.Notebook(root)
        setup_tabs(self.tabs, self)
        self.tabs.pack(fill="both", expand=1)

        # Message log at the bottom
        self.message_frame = ttk.Frame(root)
        self.message_frame.pack(fill="x", side="bottom")
        self.message_listbox = tk.Listbox(
            self.message_frame, height=5, selectmode=tk.SINGLE
        )
        self.message_listbox.pack(fill="both", expand=1)

    def setup_main_menu(self):
        """
        Set up the main menu for the application.

        Adds a 'File' menu with a 'Quit' submenu to exit the application.
        """
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Quit", command=self.quit_application)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def quit_application(self):
        """
        Quit the application cleanly.
        """
        self.root.quit()

    def append_message(self, message):
        """
        Append a message to the message log and update the message listbox.

        Args:
            message (str): The message to log and display.
        """
        self.message_log.append(message)
        self.message_listbox.insert(tk.END, message)

    def list_serial_ports(self):
        """
        Return a list of available serial ports.

        This method queries the system for connected serial devices and lists
        their device names.

        Returns:
            list of str: A list of device names for available serial ports.

        Example:
            ports = self.list_serial_ports()
            print(ports)
            # Output: ["/dev/ttyUSB0", "/dev/ttyUSB1"]
        """
        return [port.device for port in serial.tools.list_ports.comports()]

    def read_response(self):
        """
        Read the response from the printer via the serial connection.

        This method continuously reads lines from the printer until a response
        containing 'ok' or 'error' is received, indicating the end of the response.

        Returns:
            list of str: A list of lines received as a response from the printer.

        Example:
            response = app.read_response()
            print(response)
            # Output: ["ok T:200 /200", "ok"]
        """
        if not self.serial_connection:
            return []

        # Read the data from the printer (response to G-codes)
        response = []
        try:
            # Let's assume we're reading until we receive a complete response
            while True:
                line = self.serial_connection.readline().decode("utf-8").strip()
                if line:
                    response.append(line)
                if "ok" in line.lower() or "error" in line.lower():
                    break
        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
        return response


def create_app():
    """
    Create the Tkinter root window and initialize the PrinterControlApp.

    Returns:
        PrinterControlApp: An instance of the PrinterControlApp initialized with a root window.
    """
    root = tk.Tk()
    root.title("3D Printer Control")
    app_instance = PrinterControlApp(root)
    return app_instance


if __name__ == "__main__":
    app = create_app()
    app.root.mainloop()
