import socket
import json
import time

NUM_LEDS = 402
HOST = '100.85.4.50'  # Your Raspberry Pi Tailscale IP
PORT = 5000
FRAME_DELAY = 0.2  # seconds per frame (~5 FPS)

def connect():
    """Try to connect to the Pi and return a (writer, socket) tuple."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    writer = sock.makefile('w')
    return writer, sock

frame = 0

while True:
    try:
        print(f"Connecting to {HOST}:{PORT} ...")
        writer, sock = connect()
        print("Connected.")

        while True:
            # Build the LED color frame (snake animation)
            color_map = [
                [0, 0, 255] if i == frame % NUM_LEDS else [25, 0, 0]
                for i in range(NUM_LEDS)
            ]

            # Send JSON data
            writer.write(json.dumps(color_map) + '\n')
            writer.flush()

            frame += 1
            time.sleep(FRAME_DELAY)

    except (ConnectionResetError, BrokenPipeError, socket.error) as e:
        print("⚠️ Disconnected or failed to send. Reconnecting in 2s...", e)
        time.sleep(2)
    finally:
        try:
            sock.close()
        except:
            pass
