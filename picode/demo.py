#!/user/bin/env python

import serial
import sys
import math
import time
import numpy as np
import threading
import vision
    
class robot:
    def __init__(self, port="/dev/ttyACM0"):
        self.wheelbase = 0.157
        self.wheel_circumference = 2*math.pi*0.033
        self.encoder_segments = 32
        #self.s = serial.Serial(port,115200,timeout=1)
        self.s = None
        self.v_l = 0
        self.v_r = 0
        self.pd_thread = threading.Thread(target=self.visual_pd_loop, name="pd_thread")
        self.vision_thread = threading.Thread(target=vision.start_thread, name="vision_thread")
        self.serial_sem = threading.Semaphore()
        self.prev_error = 0
        
    """
    def vel_to_pwm_l(self, vel):
        
        if vel < 0:
            #return 662.15*vel - 59.873
            return 676.52*vel - 71.921
        if vel > 0:
            #return 637.09*vel + 51.57
            return 675.09*vel + 79.807
        return 0
        
    def vel_to_pwm_r(self, vel):
        
        if vel < 0:
            #return 608.83*vel - 68.259
            return 687.99*vel - 68.317
        if vel > 0:
            #return 619.95*vel + 60.407
            return 695.55*vel + 66.464        
        return 0
    """
        
    def visual_pd_loop(self):
        while (True):
            error = vision.get_error()
            print(error)
            delta_error = error - self.prev_error
            self.prev_error = error
            delta_v = -self.K*error -self.B*delta_error
            
            """
            self.v_l += delta_error/2
            self.v_r -= delta_error/2
            self.activate_motors(self.v_l, self.v_r)
            time.sleep(.05)
            """
            
    def start_demo(self, turn_direction):
        self.v_l = 0.2
        self.v_r = 0.2
        self.pd_thread.start()
        self.vision_thread.start()
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
    
    #r.activate_motors(v, v)
    r.vision_thread.start()
    time.sleep(3)
    r.pd_thread.start()
    input()
    
    r.stop()
    
__main__()