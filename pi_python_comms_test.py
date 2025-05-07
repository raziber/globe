import serial
import time
import sys
import termios
import tty

# ---- Setup UART ----
ser = serial.Serial("/dev/serial0", 9600)
time.sleep(2)  # Give Arduino time to reset

print("Connected. Press 's' to send, 'q' to quit.")

# ---- Function to read a single key without Enter ----
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return key

# ---- Main Loop ----
try:
    while True:
        key = get_key()

        if key == 's':
            ser.write(b'Hello from Pi\n')
            print("[SENT] Hello from Pi")
        elif key == 'q':
            print("Exiting...")
            break
finally:
    ser.close()
    print("Serial connection closed.")

