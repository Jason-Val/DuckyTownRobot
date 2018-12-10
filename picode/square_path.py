#!/user/bin/env python

import serial
import sys
import math
import time
import numpy as np

wheelbase = .157 #m
wheel_radius = 0.035525 #m

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
        self.encoder_segments = 32
        self.s = serial.Serial(port,115200, timeout=1)
        self.loc = [0, 0, 0]
        self.heading = 0
        self.next_loc = [0, 0]
        self.next_heading = [0, 0]
        self.l_rpm = 0
        self.r_rpm = 0
        
    def get_actual_translation(self):
        print("get translation: ")
        input()
        self._send_to_arduino("6")
        msg = self.s.read_until().decode('utf-8')
        print("received " + msg)
        input()
        if msg == '':
            return None
        _, l_count, r_count = map(int, msg.split(" "))
        l_distance = l_count*self.wheel_circumference/self.encoder_segments
        r_distance = r_count*self.wheel_circumference/self.encoder_segments
        return (l_distance, r_distance)
        
    
    def plot_pwm_vs_velocity(self, time_per_speed, pwm_list):
        velocities = [[0,0] for x in pwm_list]
        for i in range(len(pwm_list)):
            self.activate_motors(0, 0)
            time.sleep(5)
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            self.activate_motors(pwm, pwm)
            print("start sleeping...")
            time.sleep(.5)
            print("take measurement...")
            l_trans_start, r_trans_start = self.get_actual_translation()
            start_time = time.time()
            time.sleep(time_per_speed)
            print("end measurement")
            l_trans, r_trans = self.get_actual_translation()
            t = time.time()
            v_l = (l_trans - l_trans_start)/(t - start_time)
            v_r = (r_trans - r_trans_start)/(t - start_time)
            print("v is {}, {}".format(v_l, v_r))
            velocities[i][0] = v_l
            velocities[i][1] = v_r

        self.activate_motors(0, 0)
        return velocities
        
        """
        
        """
        
    def plot_pwm_vs_velocity_r(self, time_per_speed, pwm_list):
        velocities = [None for x in pwm_list]
        for i in range(len(pwm_list)):
            self.activate_motors(0, 0)
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            self.activate_motors(0, pwm)
            print("start sleeping...")
            time.sleep(2)
            print("take measurement...")
            l_trans_start, r_trans_start = self.get_actual_translation()
            start_time = time.time()
            time.sleep(time_per_speed)
            print("end measurement")
            l_trans, r_trans = self.get_actual_translation()
            t = time.time()
            v = (l_trans - l_trans_start)/(t - start_time)
            print("v is " + str(v))
            velocities[i] = v

        self.activate_motors(0, 0)
        return velocities
        
    def read_out_location(self, lpwm, rpwm, t):
        self._send_to_arduino("1 {0} {1}".format(lpwm, rpwm))
        t_init = time.time()
        while (time.time() - t_init < t):
            l_trans, r_trans = self.get_actual_translation()
            delta_x = (l_trans + r_trans)/2
            heading = math.atan2((r_trans - l_trans)/2, self.wheelbase/2)
            self.loc = [delta_x*math.cos(heading), delta_x*math.sin(heading), heading]
            print(self.loc)
            
    """
    def loop_pd():
        read_or_timeout() #updates loc[], heading
        adjustment[L, R] = pd(self.loc, self.next_loc, self.next_heading)
        command(adjustment[0] + self.l_rpm)
    """
        
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
        
    def activate_motors(self, left, right):
        #self.s.write("7 {0};".format(left).encode('utf-8'))
        #self.s.flush()
        pass
        
    def _send_to_arduino(self,cmd):
        self.s.write(cmd.encode('utf-8'))
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
    
    #r = robot("\\.\COM3")
    r = robot(port)

    time.sleep(2)
    time.sleep(2)
    #distance to drive in meters
    distance = 0.4
    #speed in meters per second
    speed = 1/4
    #rotations per second
    rotate_time = .5
    
    pwm_list = [x for x in range(0, 401, 50)]
    #pwm_list = [150, 200, 250]
    #v_r = r.plot_pwm_vs_velocity_r(3, pwm_list)
    #v_l = r.plot_pwm_vs_velocity_l(3, pwm_list)
    
    v_list = r.plot_pwm_vs_velocity(1.5, pwm_list)
    
    print(pwm_list)
    print("velocities:")
    print(v_list);
    
__main__()