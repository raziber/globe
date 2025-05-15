import serial
import wave

PORT = '/dev/ttyACM0'  # Replace if needed
BAUD = 115200
FILENAME = 'file.wav'

with wave.open(FILENAME, 'rb') as wf:
    assert wf.getsampwidth() == 2     # 16-bit
    assert wf.getframerate() == 8000  # Must match ESP32
    assert wf.getnchannels() == 1     # Mono

    ser = serial.Serial(PORT, BAUD)
    print(f"Playing {FILENAME}...")

    while chunk := wf.readframes(256):
        ser.write(chunk)

    ser.close()
    print("Done.")

