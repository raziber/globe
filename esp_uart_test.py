import serial

ser = serial.Serial('/dev/ttyACM0', 115200)

print("Reading audio stream...")
while True:
    data = ser.read(2)  # Read one 16-bit sample (2 bytes)
    sample = int.from_bytes(data, byteorder='little', signed=True)
    print(sample)

