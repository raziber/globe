import serial
import time

ser = serial.Serial("/dev/serial10", 9600)
time.sleep(2);

ser.write(b'Hello from Raspberry Pi\n')
while ser.in_waiting:
	print(ser.readline().decode())


ser.close()