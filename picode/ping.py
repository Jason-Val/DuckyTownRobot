
import sys
import serial

port_ext = "ACM0"
if len(sys.argv) > 1:
    port_ext = sys.argv[1]
port = "/dev/tty" + port_ext
rate = 9600

s1 = serial.Serial(port,rate)
s1.reset_input_buffer()
s1.read_until()
s1.write("0".encode('utf-8'))
s1.reset_input_buffer()

while (True):
    print(s1.read_until())
