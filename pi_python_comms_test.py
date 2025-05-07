import serial
import time

ser = serial.Serial("/dev/serial0", 9600)
time.sleep(2);

ser.write(b'Hello from Raspberry Pi\n')
print("message sent")

ser.close()
