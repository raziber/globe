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

def send_to_socket(data, writer=None, sock=None, reconnect=True):
    """
    Send JSON data to a socket connection.
    Returns (success, writer, sock)

    ALWAYS send data of the format:
    [
        [R, G, B],  // LED 0
        [R, G, B],  // LED 1
        ...
        [R, G, B]   // LED 401
    ]

    total 402 LEDs
    don't send more or less or anything else
    """
    print(f"Sending data to socket")
    if writer is None or sock is None:
        try:
            writer, sock = connect()
            print(f"Connected to {HOST}:{PORT}")
        except socket.error as e:
            print(f"⚠️ Failed to connect: {e}")
            return False, None, None

    try:
        print("writing")
        writer.write(json.dumps(data) + '\n')
        print("flushing")
        writer.flush()
        return True, writer, sock
    except (ConnectionResetError, BrokenPipeError, socket.error) as e:
        print(f"⚠️ Failed to send data: {e}")
        if reconnect:
            try:
                sock.close()
            except:
                pass
            return send_to_socket(data, None, None, reconnect)
        return False, None, None

# try:
#     frame = 0
#     while True:
#         print(f"Connecting to {HOST}:{PORT} ...")
#         writer, sock = connect()
#         print("Connected.")

#         while True:
#             color_map = [
#                 [255, 255, 255] if i == frame % NUM_LEDS else [25, 0, 0]
#                 for i in range(NUM_LEDS)
#             ]

#             success, writer, sock = send_to_socket(color_map, writer, sock)
#             if not success:
#                 break  # reconnect

#             frame += 1
#             time.sleep(FRAME_DELAY)

# except KeyboardInterrupt:
#     print("\n🛑 Stopped by Ctrl+C")

# finally:
#     try:
#         sock.close()
#     except:
#         pass
