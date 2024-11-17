import tkinter as tk
from tkinter import ttk
import serial
from ui.tab_manager import setup_tabs
import serial.tools.list_ports

class PrinterControlApp:
    def __init__(self, root):
        self.root = root
        self.serial_connection = None
        self.message_log = []
        
        # Set up the tab interface
        self.tabs = ttk.Notebook(root)
        setup_tabs(self.tabs, self)
        self.tabs.pack(fill="both", expand=1)

        # Message log at the bottom
        self.message_frame = ttk.Frame(root)
        self.message_frame.pack(fill="x", side="bottom")
        self.message_listbox = tk.Listbox(self.message_frame, height=5, selectmode=tk.SINGLE)
        self.message_listbox.pack(fill="both", expand=1)

    def append_message(self, message):
        """Append a message to the log."""
        self.message_log.append(message)
        self.message_listbox.insert(tk.END, message)

    def list_serial_ports(self):
        """Return a list of available serial ports."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def read_response(self):
        """Read the response from the printer."""
        if not self.serial_connection:
            return []

        # Read the data from the printer (response to G-codes)
        response = []
        try:
            # Let's assume we're reading until we receive a complete response
            while True:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    response.append(line)
                if 'ok' in line.lower() or 'error' in line.lower():  # Assuming we use 'ok'/'error' to mark the end of response
                    break
        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
        return response


def create_app():
    root = tk.Tk()
    root.title("3D Printer Control")
    app = PrinterControlApp(root)
    return app

if __name__ == "__main__":
    app = create_app()
    app.root.mainloop()
