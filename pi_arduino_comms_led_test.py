import serial
import time

PORT = "/dev/ttyS0"
BAUD = 115200
NUM_LEDS = 409
DELAY = 0.1  # Safe delay

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

def send_frame():
    frame = bytearray()
    # Frame header: [0xAA, 0x55, high_byte, low_byte]
    payload_len = NUM_LEDS * 3  # 1227
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    for i in range(NUM_LEDS):
        if i < 221:
            r, g, b = 0, 255, 0  # Green
        else:
            r, g, b = 0, 0, 255  # Blue
        frame.extend([r, g, b])

    ser.write(frame)

while True:
    send_frame()
    time.sleep(DELAY)

