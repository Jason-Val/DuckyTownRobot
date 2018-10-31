#!/user/bin/env python

import serial
import sys
import math
import time

wheelbase = .157 #m
wheel_radius = 0.033 #m

class robot:
    def __init__(self, port = "/dev/ttyACM0"):
        self.wheelbase = 0.157
        self.wheel_circumference = 2*math.pi*0.033
        self.s = serial.Serial(port,9600)
        
    def drive_straight(self, distance, speed):
        print("***Drive Straight***")
        print("rpm is: {}".format(self._speed_to_rpm(speed)))
        rpm = int(self._speed_to_rpm(speed))
        self._send_to_arduino("1 {0} {1}".format(rpm, rpm))
        print("sleep for {}".format(distance/speed))
        time.sleep(distance/speed)
        self._send_to_arduino("1 0 0")
        
    def rotate(self, angle, delta_time):
        print("***Rotate***")
        distance = self._angle_to_distance(angle)
        print("distance is ", distance)
        
        speed = distance/delta_time
        print("speed is ", speed)
        wheel_rpm = int(self._speed_to_rpm(speed))
        
        print("Wheel rpm is {}".format(wheel_rpm))
        self._send_to_arduino("1 {0} {1}".format(-wheel_rpm, wheel_rpm))
        print("sleep for {}".format(delta_time))
        self._sleep(delta_time)
        self._send_to_arduino("1 0 0".format(-wheel_rpm, wheel_rpm))
        
    def stop(self):
        self._send_to_arduino("1 0 0")
        self.s.close()
        
    def _sleep(self, t):
        start = time.time()
        while (time.time() - start < t):
            pass
        
    def _send_to_arduino(self,cmd):
        self.s.write((cmd + ".").encode('utf-8'))
        
    def _speed_to_rpm(self, speed):
        return 60.0*speed/self.wheel_circumference #rpm
                
    #angle in radians
    def _angle_to_distance(self, angle):
        return (self.wheelbase/2)*angle
    
    
def __main__():
    port_ext = "ACM0"
    if len(sys.argv) > 1:
        port_ext = sys.argv[1]
    port = "/dev/tty" + port_ext
    
    r = robot(port)
    time.sleep(2)
    #distance to drive in meters
    distance = 0.4
    #speed in meters per second
    speed = 1/4
    #rotations per second
    rotate_time = .5
    
    print("begin driving")
    for i in range(4):
        r.drive_straight(distance, speed)
        r.rotate(math.pi/2, rotate_time)
    
    r.stop()
    
__main__()