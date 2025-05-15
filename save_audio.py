import serial
import wave

PORT = '/dev/ttyACM0'
BAUD = 115200
SAMPLE_RATE = 8000
DURATION_SEC = 5
FILENAME = 'mic.wav'

ser = serial.Serial(PORT, BAUD)
print(f"Recording {DURATION_SEC} seconds...")

num_samples = SAMPLE_RATE * DURATION_SEC
data = ser.read(2 * num_samples)  # 2 bytes/sample

print(f"Saving to {FILENAME}...")
with wave.open(FILENAME, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(data)

print("Done.")

