#!/user/bin/env python

import serial
import sys
import math
import time
import matplotlib.pyplot as plt
import numpy as np

wheelbase = .157 #m
wheel_radius = 0.033 #m

"""
central thread; controls arduino
read thread:
 >constantly reads
 >updates ping value
 >adjusts motors based on PID (and interrupts)
"""

class robot:
    def __init__(self, port = "/dev/ttyACM0"):
        self.wheelbase = 0.157
        self.wheel_circumference = 2*math.pi*0.033
        self.encoder_segments = 16
        self.s = serial.Serial(port,9600)
        self.loc = [0, 0]
        self.heading = 0
        self.next_loc = [0, 0]
        self.next_heading = [0, 0]
        self.l_rpm = 0
        self.r_rpm = 0
        
    def get_actual_translation(self, i):
        msg = self.s.read_until().decode('utf-8')
        print(msg)
        _, l_count, r_count = map(int, msg.split(" "))
        l_distance = l_count*self.wheel_circumference/self.encoder_segments
        r_distance = r_count*self.wheel_circumference/self.encoder_segments
        return (l_distance, r_distance)
        
    def test_straight_line(self, time_per_speed, pwm_list):
        velocities = [[None, None] for x in pwm_list]
        l_trans_start = 0
        r_trans_start = 0
        for i in range(len(pwm_list)):
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            l_trans = 0
            r_trans = 0
            self._send_to_arduino("1 {0} {0}".format(pwm))
            start_time = time.time()
            t = start_time
            while (t < start_time + time_per_speed):
                l_trans, r_trans = self.get_actual_translation(i)
                t = time.time()
            velocities[i][0] = (l_trans - l_trans_start)/(t - start_time)
            velocities[i][1] = (r_trans - r_trans_start)/(t - start_time)
        self._send_to_arduino("1 0 0")
        return velocities
        
    def loop_pd():
        read_or_timeout() #updates loc[], heading
        adjustment[L, R] = pd(self.loc, self.heading, self.next_loc, self.next_heading)
        command(adjustment[0] + self.l_rpm)
        
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
        self.s.flush()
        
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
    
    r = robot("\\.\COM3")
    time.sleep(2)
    #distance to drive in meters
    distance = 0.4
    #speed in meters per second
    speed = 1/4
    #rotations per second
    rotate_time = .5
    
    pwm_high = [x for x in range(50, 401, 50)]
    pwm_low = [x for x in range(-400, -49, 50)]
    v_high = r.test_straight_line(1, pwm_high)
    v_low = r.test_straight_line(1, pwm_low)
    r.stop()
    
    v_l = []
    v_r = []
    
    for l, r in (v_low + v_high):
        v_l.append(l)
        v_r.append(r)
        
    print(pwm_low + pwm_high)
    print(v_l)
    
    plt.plot(pwm_low + pwm_high, v_l, label="left motor")
    plt.plot(pwm_low + pwm_high, v_r, label="right motor")
    
    plt.xlabel("pwm")
    plt.ylabel("velocity (m/s)")
    plt.title("velocity vs pwm")
    plt.legend()
    
    plt.show()
    
    """
    print("begin driving")
    for i in range(4):
        r.drive_straight(distance, speed)
        r.rotate(math.pi/2, rotate_time)
    r.stop()
    """
    
__main__()