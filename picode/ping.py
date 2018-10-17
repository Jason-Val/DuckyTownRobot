
import serial
port = "/dev/ttyACM1"
rate = 9600

s1 = serial.Serial(port,rate)
s1.flushInput()

while (True):
    print(s1.read_until().decode("utf-8"))
