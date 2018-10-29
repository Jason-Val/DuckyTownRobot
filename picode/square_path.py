#!/user/bin/env python

#import serial
import sys
import math
import time

wheelbase = .157 #m
wheel_radius = 0.033 #m

class robot:
    def __init__(self, port = "/dev/ttyACM0"):
        self.wheelbase = 0.157
        self.wheel_circumference = 2*pi*0.033
        self.s = serial.Serial(port,rate)
        
    def drive_straight(distance, speed):
        self.s.write("1 {0} {0}".format(self._speed_to_rpm(speed)).encode('utf-8'))
        time.sleep(distance/speed)
        self.s.write("1 {0} {0}".format(0).encode('utf-8'))
        
    def rotate(angle, rps):
        distance = self._angle_to_distance(angle)
        speed = self.circumference*rps
        delta_time = distance/speed
        wheel_rpm = self._speed_to_rpm(speed)
        
        print(wheel_rpm)
        s.write("1 {0} {1}".format(-wheel_rpm, wheel_rpm).encode('utf-8'))
        time.sleep(delta_time)
        s.write("1 {0} {0}".format(0, 0).encode('utf-8'))
        
    def _speed_to_rpm(self, speed):
        return 60*speed/self.circumference #rpm
                
    #angle in radians
    def _angle_to_distance(angle):
        #circumference = 2*math.pi*(self.wheelbase/2) #circumference of circle with diameter=wheelbase
        #return circumference*angle/(2*math.pi)
        return (self.wheelbase/2)*angle
    
    
def __main__():
    port_ext = "ACM0"
    if len(sys.argv) > 1:
        port_ext = sys.argv[1]
    port = "/dev/tty" + port_ext
    
    r = robot(port)
        
    #distance to drive in meters
    distance = 0.4
    #speed in meters per second
    speed = 1/10
    #rotations per second
    rotate_speed = 1/8
    
    for i in range(4):
        r.drive_straight(distance, speed)
        r.rotate(math.pi, rotate_speed)
    
__main__()