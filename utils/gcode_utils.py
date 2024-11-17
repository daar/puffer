def send_gcode(serial_connection, gcode, callback=None):
    if serial_connection:
        serial_connection.write(f"{gcode.strip()}\n".encode())
        if callback:
            callback(f"Sent: {gcode}")

def parse_gcode_response(serial_connection):
    response = []
    if serial_connection:
        while serial_connection.in_waiting > 0:
            line = serial_connection.readline().decode().strip()
            response.append(line)
    return response
