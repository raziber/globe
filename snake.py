import serial
import time

PORT = "/dev/ttyS0"
BAUD = 115200
NUM_LEDS = 409
SNAKE_LENGTH = 25
DELAY = 0.1  # ~10 FPS

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

snake_start = 0

def send_frame():
    global snake_start
    frame = bytearray()

    # Header: [0xAA, 0x55, len_hi, len_lo]
    payload_len = NUM_LEDS * 3  # 1227
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    for i in range(NUM_LEDS):
        # Determine if current LED is inside the snake range
        in_snake = (snake_start <= i < snake_start + SNAKE_LENGTH) or \
                   (snake_start + SNAKE_LENGTH > NUM_LEDS and i < (snake_start + SNAKE_LENGTH) % NUM_LEDS)

        if in_snake:
            r, g, b = 255, 0, 0  # Red snake
        else:
            r, g, b = 0, 0, 255  # Blue background

        frame.extend([r, g, b])

    ser.write(frame)

    # Advance snake
    snake_start = (snake_start + 1) % NUM_LEDS

while True:
    send_frame()
    time.sleep(DELAY)

