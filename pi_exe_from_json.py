import serial
import time
import json
import os

PORT = '/dev/ttyAMA0'
BAUD = 115200
NUM_LEDS = 402
JSON_PATH = 'led_output.json'
REFRESH_DELAY = 0.05  # seconds between updates

def load_led_data():
    if not os.path.exists(JSON_PATH):
        return [(0, 0, 0)] * NUM_LEDS  # fallback to all off

    try:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)

        if data.get("type") != "fullmap":
            return [(0, 0, 0)] * NUM_LEDS  # not a full frame

        color_map = [(0, 0, 0)] * NUM_LEDS
        for pixel in data["pixels"]:
            idx = pixel["id"]
            rgb = pixel.get("color_rgb", [0, 0, 0])
            if 0 <= idx < NUM_LEDS:
                color_map[idx] = tuple(rgb)
        return color_map
    except Exception as e:
        print(f"⚠️ Failed to read LED data: {e}")
        return [(0, 0, 0)] * NUM_LEDS

def send_frame(ser, color_map):
    payload_len = NUM_LEDS * 3
    frame = bytearray()
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    for r, g, b in color_map:
        frame.extend([r, g, b])

    ser.write(frame)

def main():
    print(f"📡 Opening serial port {PORT} at {BAUD}...")
    ser = serial.Serial(PORT, BAUD)
    time.sleep(2)  # Allow serial to stabilize

    print("🎛️ Starting LED output loop...")
    while True:
        color_map = load_led_data()
        send_frame(ser, color_map)
        time.sleep(REFRESH_DELAY)

if __name__ == "__main__":
    main()
