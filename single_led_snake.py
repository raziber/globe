import serial
import time
import sys
import select
import tty
import termios

PORT = '/dev/ttyAMA0'
BAUD = 115200
NUM_LEDS = 409
SNAKE_LENGTH = 1

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

snake_start = 0

def send_frame():
    frame = bytearray()
    payload_len = NUM_LEDS * 3
    frame.extend([0xAA, 0x55, (payload_len >> 8) & 0xFF, payload_len & 0xFF])

    for i in range(NUM_LEDS):
        in_snake = (snake_start <= i < snake_start + SNAKE_LENGTH) or \
                   (snake_start + SNAKE_LENGTH > NUM_LEDS and i < (snake_start + SNAKE_LENGTH) % NUM_LEDS)

        if in_snake:
            r, g, b = 255, 0, 0
        else:
            r, g, b = 0, 0, 3

        frame.extend([r, g, b])

    ser.write(frame)
    print(f"Snake starts at LED index: {snake_start}")

def key_pressed():
    return select.select([sys.stdin], [], [], 0)[0]

# Save terminal settings
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

try:
    tty.setcbreak(fd)  # set terminal to raw mode
    print("Press 'd' to move forward, 'a' to move backward. Ctrl+C to quit.")

    while True:
        if key_pressed():
            key = sys.stdin.read(1)

            if key == 'd':
                snake_start = (snake_start + 1) % NUM_LEDS
                send_frame()
            elif key == 'a':
                snake_start = (snake_start - 1) % NUM_LEDS
                send_frame()

finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

