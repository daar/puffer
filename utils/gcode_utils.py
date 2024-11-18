"""
Module for sending G-code commands and parsing responses.

This module provides utility functions to send G-code commands to a connected
3D printer via a serial connection and to parse responses received from the printer.
"""

def send_gcode(serial_connection, gcode, callback=None):
    """
    Send a G-code command to the 3D printer via the serial connection.

    This function writes a G-code command to the printer through the provided
    serial connection. Optionally, a callback function can be used to log or
    display the sent command.

    Args:
        serial_connection (serial.Serial): The serial connection to the printer.
        gcode (str): The G-code command to send. It will be stripped of whitespace.
        callback (function, optional): A function to handle logging or other actions 
                                        after sending the command. It receives a string 
                                        argument with the sent G-code message.

    Example:
        send_gcode(serial_conn, "M105", print)
        # Output: Sent: M105
    """
    if serial_connection:
        serial_connection.write(f"{gcode.strip()}\n".encode())
        if callback:
            callback(f"Sent: {gcode}")


def parse_gcode_response(serial_connection):
    """
    Parse the response from the 3D printer after sending G-code commands.

    This function reads lines from the serial connection until all available
    data is retrieved and decodes each line. The response is returned as a list
    of strings, with each line of the response as a separate item.

    Args:
        serial_connection (serial.Serial): The serial connection to the printer.

    Returns:
        list of str: A list of response lines received from the printer.

    Example:
        response = parse_gcode_response(serial_conn)
        print(response)
        # Output: ["ok T:210 /210 B:60 /60", "echo:busy processing"]
    """
    response = []
    if serial_connection:
        while serial_connection.in_waiting > 0:
            line = serial_connection.readline().decode().strip()
            response.append(line)
    return response
