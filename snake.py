import serial
import time

PORT = '/dev/ttyAMA0'
BAUD = 115200
NUM_LEDS = 409
DELAY = 0.01  # Safe delay

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

snake_start = 0
SNAKE_LENGTH = 20

def send_frame():
    global snake_start
    frame = bytearray()
    # Frame header: [0xAA, 0x55, high_byte, low_byte]
    payload_len = NUM_LEDS * 3  # 1227
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    for i in range(NUM_LEDS):
        # Snake wraps around
        in_snake = (snake_start <= i < snake_start + SNAKE_LENGTH) or \
                   (snake_start + SNAKE_LENGTH > NUM_LEDS and i < (snake_start + SNAKE_LENGTH) % NUM_LEDS)

        if in_snake:
            r, g, b = 100, 0, 0  # Red snake
        else:
            r, g, b = 0, 0, 6  # Blue background

        frame.extend([r, g, b])

    ser.write(frame)
    snake_start = (snake_start + 4) % NUM_LEDS

while True:
    send_frame()
    time.sleep(DELAY)

