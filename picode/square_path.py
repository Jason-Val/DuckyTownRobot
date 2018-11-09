#!/user/bin/env python

import serial
import sys
import math
import time
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
        self.encoder_segments = 32
        self.s = serial.Serial(port,115200,timeout=1)
        self.loc = [0, 0, 0]
        self.heading = 0
        self.next_loc = [0, 0]
        self.next_heading = [0, 0]
        self.l_rpm = 0
        self.r_rpm = 0
        
    def get_actual_translation(self):
        self._send_to_arduino("2")
        msg = self.s.read_until().decode('utf-8')
        print("received " + msg)
        if msg == '':
            return None
        _, l_count, r_count = map(int, msg.split(" "))
        l_distance = l_count*self.wheel_circumference/self.encoder_segments
        r_distance = r_count*self.wheel_circumference/self.encoder_segments
        return (l_distance, r_distance)
        
    def plot_pwm_vs_velocity(self, time_per_speed, pwm_list):
        velocities = [[None, None] for x in pwm_list]
        l_trans_start = 0
        r_trans_start = 0
        for i in range(len(pwm_list)):
            self.activate_motors(0, 0)
            time.sleep(5)
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            self.activate_motors(pwm, pwm)
            time.sleep(2)
            print("start sleeping...")
            l_trans_start, r_trans_start = self.get_actual_translation()
            start_time = time.time()
            time.sleep(time_per_speed)
            print("end sleeping")
            l_trans, r_trans = self.get_actual_translation()
            t = time.time()
            
            velocities[i][0] = (l_trans - l_trans_start)/(t - start_time)
            velocities[i][1] = (r_trans - r_trans_start)/(t - start_time)

        self.activate_motors(0, 0)
        return velocities
        
    def plot_pwm_vs_velocity_l(self, time_per_speed, pwm_list):
        velocities = [None for x in pwm_list]
        for i in range(len(pwm_list)):
            self.activate_motors(0, 0)
            #time.sleep(5)
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            self.activate_motors(pwm, 0)
            print("start sleeping...")
            time.sleep(2)
            print("take measurement...")
            l_trans_start, r_trans_start = self.get_actual_translation()
            start_time = time.time()
            time.sleep(time_per_speed)
            print("end measurement")
            l_trans, r_trans = self.get_actual_translation()
            t = time.time()
            v = (r_trans - r_trans_start)/(t - start_time)
            print("v is " + str(v))
            velocities[i] = v

        self.activate_motors(0, 0)
        return velocities
        
    def plot_pwm_vs_velocity_r(self, time_per_speed, pwm_list):
        velocities = [None for x in pwm_list]
        for i in range(len(pwm_list)):
            self.activate_motors(0, 0)
            print("test pwm {}".format(pwm_list[i]))
            pwm = pwm_list[i]
            self.activate_motors(pwm, 0)
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
        self.s.write("1 {0} {1}.".format(left, right).encode('utf-8'))
        self.s.flush()
        
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
    #distance to drive in meters
    distance = 0.4
    #speed in meters per second
    speed = 1/4
    #rotations per second
    rotate_time = .5
        
    pwm_list = [x for x in range(-400, 401, 50)]
    #v_r = r.plot_pwm_vs_velocity_r(3, pwm_list)
    v_l = r.plot_pwm_vs_velocity_l(3, pwm_list)
    print(pwm_list)
    print("Left data:")
    print(v_l)
    print("Right data:")
    print(v_r)
    
    """
    plt.plot(pwm_low + pwm_high, v_l, label="left motor")
    plt.plot(pwm_low + pwm_high, v_r, label="right motor")
    
    plt.xlabel("pwm")
    plt.ylabel("velocity (m/s)")
    plt.title("velocity vs pwm")
    plt.legend()
    
    plt.show()
    """
    """
    
    [-400, -350, -300, -250, -200, -150, -100, -50, 50, 100, 150, 200, 250, 300, 350, 400]
    [-0.5324684671734549, 
    -0.4389622757837263, 
    -0.3775627211935226, 
    -0.2934385012961068, 
    -0.20666704113785078, 
    -0.13562950021804568, 
    -0.05161557481842923, 
    0.0, 
    0.0, 
    0.07103386441256744, 
    0.16162422284479072, 
    0.23697108656593577, 
    0.3121389160862959, 
    0.39175563657950613, 
    0.47138180138081637, 
    0.5335317438787168]
    
    print("begin driving")
    for i in range(4):
        r.drive_straight(distance, speed)
        r.rotate(math.pi/2, rotate_time)
    r.stop()
    """
    
__main__()