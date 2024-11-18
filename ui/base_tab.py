"""
Module for creating and managing tabs in a Tkinter notebook widget.

This module provides the `BaseTab` class, which acts as a base for adding
tabs to a Tkinter `ttk.Notebook` widget. Each tab is represented by a 
`ttk.Frame` widget that is automatically added to the notebook with a specified name.
"""

from utils.gcode_utils import send_gcode, parse_gcode_response


class BaseTab:
    """
    A base class for handling common functionality in printer control tabs.

    Provides methods to log messages, check the printer connection, set status messages,
    and manage periodic tasks.
    """
    def __init__(self, tabs, app, tab_name):
        """
        Initialize a BaseTab instance.

        Args:
            tabs (ttk.Notebook): The notebook widget to add the tab to.
            app (Any): The application context or instance associated with the tab.
            tab_name (str): The display name of the tab.
        """
        self.tabs = tabs
        self.app = app
        self.tab_name = tab_name
        self.frame = ttk.Frame(tabs)
        self.tabs.add(self.frame, text=tab_name)
        self.update_periodic_tasks()

    def log_message(self, message):
        """
        Log a message to the app's message listbox.
        """
        self.app.append_message(message)

    def check_printer_connection(self):
        """
        Check if the app's serial connection is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        if not self.app.serial_connection:
            self.set_status_message("Error: No printer connected.", error=True)
            return False
        return True

    def set_status_message(self, message, error=False):
        """
        Set a status message on the UI.

        Args:
            message (str): The message to display.
            error (bool): Whether the message is an error.
        """
        if error:
            self.frame.configure(bg="red")
        else:
            self.frame.configure(bg="green")
        self.app.set_status(message)

    def update_periodic_tasks(self):
        """
        Schedule tasks to update periodically, e.g., temperature readings.
        """
        self.frame.after(1000, self.update_periodic_tasks)

    def send_and_receive_gcode(self, gcode, response_marker):
        """
        Send a G-code command and wait for a response.

        Args:
            gcode (str): The G-code command to send.
            response_marker (str): A keyword to search for in the response.

        Returns:
            str: The response message.
        """
        send_gcode(self.app.serial_connection, gcode, self.app.append_message)
        response = parse_gcode_response(self.app.serial_connection)
        for line in response:
            if response_marker in line:
                return line
        return None
