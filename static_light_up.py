import serial
import time

PORT = '/dev/ttyAMA0'
BAUD = 115200
NUM_LEDS = 402
GROUP_SIZE = 20
BRIGHTNESS = 30  # Scale to 30 out of 255

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

def scale_color(r, g, b, brightness):
    factor = brightness / 255.0
    return int(r * factor), int(g * factor), int(b * factor)

def send_rgb_groups():
    frame = bytearray()
    payload_len = NUM_LEDS * 3
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    colors = [
        (255, 0, 0),   # Red
        (0, 0, 255),   # Blue
        (0, 255, 0),   # Green
    ]

    for i in range(NUM_LEDS):
        group_index = (i // GROUP_SIZE) % len(colors)
        r, g, b = colors[group_index]
        r, g, b = scale_color(r, g, b, BRIGHTNESS)
        frame.extend([r, g, b])

    # Send to UART
    ser.write(frame)

    # Save frame to file
    with open("uart_debug_frame.bin", "wb") as f:
        f.write(frame)

send_rgb_groups()

