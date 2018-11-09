#!/user/bin/env python

import serial
import sys
import math
import time
import numpy as np
import threading
#import vision
    
class robot:
    def __init__(self, port = "/dev/ttyACM0"):
        self.wheelbase = 0.157
        self.wheel_circumference = 2*math.pi*0.033
        self.encoder_segments = 32
        self.s = serial.Serial(port,115200,timeout=1)
        self.s = None
        self.v_l = 0
        self.v_r = 0
        self.pd_thread = threading.Thread(target=self.visual_pd_loop, name="pd_thread")
        #self.vision_thread = threading.Thread(target=vision.start_thread, name="vision_thread")
        self.serial_sem = threading.Semaphore()
        
    def vel_to_pwm_l(self, vel):
        if vel < 0:
            return 662.15*vel - 59.873
        if vel > 0:
            return 637.09*vel + 51.57
        return 0
        
    def vel_to_pwm_r(self, vel):
        if vel < 0:
            return 608.83*vel - 68.259
        if vel > 0:
            return 619.95*vel + 60.407
        return 0
        
    def visual_pd_loop(self):
        while (True):
            #error = vision.error()
            delta_l = 0         #TODO: Sam implement this
            delta_r = 0
            self.v_l += delta_l
            self.v_r += delta_r
            self.activate_motors(self.v_l, self.v_r)
        
    def start_demo(self, turn_direction):
        self.v_l = 0.2
        self.v_r = 0.2
        self.pd_thread.start()
        #self.vision_thread.start()
        self.activate_motors(self.v_l, self.v_r)
        while (input() != "q"):
            pass
        self.stop()
        
    def stop(self):
        self._send_to_arduino("1 0 0")
        self.s.close()
        
    def activate_motors(self, v_l, v_r):
        self._send_to_arduino("1 {0} {1}.".format(left, right))
        
    def _send_to_arduino(self, cmd):
        self.serial_sem.acquire()
        self.s.write(cmd.encode('utf-8'))
        self.s.flush()
        self.serial_sem.release()
    
def __main__():
    port_ext = "ACM0"
    if len(sys.argv) > 1:
        port_ext = sys.argv[1]
    port = "/dev/tty" + port_ext
    
    #r = robot("\\.\COM3")
    r = robot(port)

    time.sleep(2)
    
    pwm_l = r.vel_to_pwm_l(0.2)
    pwm_r = r.vel_to_pwm_r(0.2)
    print("pwm_l: {}, pwm_r: {}".format(pwm_l, pwm_r))
    r.activate_motors(pwm_l, pwm_r)
    input()
    r.stop()
    
__main__()