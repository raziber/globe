import serial
import time

# === Configuration ===
PORT = "/dev/ttyS0"     # Adjust if needed
BAUD = 115200
NUM_LEDS = 409
SNAKE_LENGTH = 25
SYNC_BYTE = 0xAA

# Estimated frame size
FRAME_SIZE = 1 + NUM_LEDS * 3  # 1 sync + 1227 RGB bytes = 1228 bytes

# Serial setup
ser = serial.Serial(PORT, BAUD)
time.sleep(2)  # Give Arduino(s) time to boot

snake_start = 0

def send_frame():
    global snake_start

    frame = bytearray()
    frame.append(SYNC_BYTE)

    for i in range(NUM_LEDS):
        in_snake = (snake_start <= i < snake_start + SNAKE_LENGTH) or \
                   (snake_start + SNAKE_LENGTH > NUM_LEDS and i < (snake_start + SNAKE_LENGTH) % NUM_LEDS)

        if in_snake:
            r, g, b = 255, 0, 0  # Red snake
        else:
            r, g, b = 0, 0, 255  # Blue background

        frame.extend([r, g, b])

    ser.write(frame)

    snake_start = (snake_start + 1) % NUM_LEDS

# === Estimate max safe FPS ===
# 115200 baud ≈ 14400 bytes/sec
# FRAME_SIZE = 1228 bytes → max FPS ≈ 11.7
MAX_FPS = 11
DELAY = 1 / MAX_FPS  # ~0.085 sec per frame

# === Main loop ===
while True:
    start_time = time.time()
    send_frame()
    elapsed = time.time() - start_time
    sleep_time = max(0, DELAY - elapsed)
    time.sleep(sleep_time)

