import serial
import time

ser = serial.Serial('/dev/ttyACM0',9600)

time.sleep(2)   # wait for Arduino reset

while True:
    ser.write(b'A')
    print("sent command")
    time.sleep(1)