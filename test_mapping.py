import serial
import time
import json

PORT = '/dev/ttyAMA0'
BAUD = 115200
NUM_LEDS = 402
DELAY = 0.1  # seconds
JSON_PATH = 'coordinates_shifted_2.json'

# Open serial port
ser = serial.Serial(PORT, BAUD)
time.sleep(2)  # allow serial to stabilize

# Load coordinate data
with open(JSON_PATH, 'r') as f:
    coordinates = json.load(f)

# Map from LED ID to its color based on phi
def build_color_map():
    color_map = [(0, 0, 0)] * NUM_LEDS  # default off
    for coord in coordinates:
        idx = coord["id"]
        phi = coord["phi"]
        theta = coord["theta"]
        if 0 <= idx < NUM_LEDS:
            if theta < 180:
                color_map[idx] = (0, 0, 55)  # blue
            else:
                color_map[idx] = (55, 0, 0)  # red
    return color_map

def send_frame():
    frame = bytearray()
    payload_len = NUM_LEDS * 3
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    color_map = build_color_map()
    for r, g, b in color_map:
        frame.extend([r, g, b])

    ser.write(frame)

# Main loop
while True:
    send_frame()
    time.sleep(DELAY)

