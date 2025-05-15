import serial
import wave

PORT = '/dev/ttyACM0'  # From dmesg
BAUD = 115200
SAMPLE_RATE = 8000     # Same as on ESP32
DURATION = 10          # seconds
FILENAME = 'mic.wav'

ser = serial.Serial(PORT, BAUD)
print(f"Recording {DURATION}s to {FILENAME}...")

num_samples = SAMPLE_RATE * DURATION
audio = bytearray()

while len(audio) < num_samples * 2:
    audio += ser.read(2)

ser.close()

# Write to WAV
with wave.open(FILENAME, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio)

print(f"Saved {FILENAME} — transfer to PC and listen 🎧")

