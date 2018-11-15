#!/user/bin/env python

import serial
import sys
import math
import time
import numpy as np
import threading
import vision

follow_lane = False
curr_error = 0

class robot:
    def __init__(self, port="/dev/ttyACM0"):
        magnitude = 10
        range = 100
        scaleK = 5.30
        scaleB = 5.00
        self.K = 1.0/(magnitude*range*scaleK)
        self.B = 1.0/(magnitude*range*scaleB)
        self.wheelbase = 0.157
        self.wheel_circumference = 2*math.pi*0.033
        self.encoder_segments = 32
        self.s = serial.Serial(port,115200,timeout=1)
        self.v_l = 0.0
        self.v_r = 0.0
        self.pd_thread = threading.Thread(target=self.visual_pd_loop, name="pd_thread")
        self.vision_thread = threading.Thread(target=vision.start_thread, name="vision_thread")
        self.serial_sem = threading.Semaphore()
        self.prev_error = 0.0
        
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
        while(vision.img == None):
            time.sleep(0.5)
            print("ZZZ")
        
        self.v_l = 0.108
        self.v_r = 0.108
        self.activate_motors(self.v_l, self.v_r)
        
        time.sleep(.1)
        
        print("***start***")
        
        while (True):
            error = vision.get_error()
            if(error == None):
                continue
            error += 12
            print(error)
            delta_error = error - self.prev_error
            #if delta_error > 40:
            #    continue
            self.prev_error = error
            delta_v = -self.K*error -self.B*delta_error
            print("delta v: {}".format(delta_v))

            global follow_lane
            global curr_error
            curr_error = error

            if(follow_lane):
                #print("Following")
                #Activate Motors here
                #self.v_l += delta_v/2.0
                #self.v_r -= delta_v/2.0
                print("vel: {}, {}".format(self.v_l + delta_v/2, self.v_r - delta_v/2))
                self.activate_motors(self.v_l + delta_v/2, self.v_r - delta_v/2)
                time.sleep(.05)
            

    def get_deltas(self):
        #TODO
        #Return delta x, delta y, delta theta
        return (0,0,0)

            
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
        self._send_to_arduino("1 0 0;")
        self.s.close()
        
    def activate_motors(self, v_l, v_r):
        self._send_to_arduino("5 {0} {1};".format(format(v_l, '.4f'), format(v_r, '.4f')))
        
    def _send_to_arduino(self, cmd):
        self.serial_sem.acquire()
        self.s.write(cmd.encode('utf-8'))
        self.s.flush()
        self.serial_sem.release()

def get_curr_error():
    global curr_error
    return curr_error

def __main__():
    port_ext = "ACM0"
    if len(sys.argv) > 1:
        port_ext = sys.argv[1]
    port = "/dev/tty" + port_ext
    
    #r = robot("\\.\COM3")
    r = robot(port)
    
    time.sleep(2)

    state = 0
    running = True
    
    #r.activate_motors(v, v)
    r.vision_thread.start()
    time.sleep(3)
    r.pd_thread.start()

    while(True):

        follow_lane = True

        while(vision.isStopSign() < 0):
            follow_lane = True
            time.sleep(0.1)

        while(vision.isStopSign() > 0):
            follow_lane = True
            time.sleep(0.1)

        self.v_l = 0.0
        self.v_r = 0.0
        r.activate_motors(r.v_l, r.v_r)
        follow_lane = False
        print("Done")
        input()

    follow_lane = False
    r.activate_motors(0, 0)
    
    r.vision_thread.join()
    r.pd_thread.join()
    
    input()
    
    # while(running):
    #     global follow_lane
    #     print("State: " + str(state))

    #     if(state == 0):
    #         #waiting to go
    #         #Do nothing until user inputs something
    #         s_in = input()
    #         if(s_in == "stop"):
    #             state = -2
    #         state += 1

    #     elif(state == 1):
    #         #First Straight Away
    #         #Line follow until we hit a left turn
    #         while(get_curr_error() < 100):
    #             follow_lane = True

    #         follow_lane = False
    #         state += 1
        
    #     elif(state == 2):
    #         #The turn itself (left)
    #         #Use the pd controller to navigate the robot around the turn
    #         r.activate_motors(1.1, 1.35)
    #         time.sleep(2.0)
    #         r.activate_motors(0, 0)
    #         state += 1

    #     elif(state == 3):
    #         #The second straight away
    #         #Use line following until we see the red
    #         while(vision.isStopSign() < 0):
    #             follow_lane = True

    #         state += 1

    #     elif(state == 4):
    #         #We are on the red
    #         #Line follow until we no longer see then red
    #         #Use pd to drive a few inches forward then print  x,y,theta

    #         while(vision.isStopSign() > 0):
    #             follow_lane = True

    #         follow_lane = False

    #         r.activate_motors(1.15, 1.15)
    #         time.sleep(1.0)
    #         r.activate_motors(0, 0)

    #         dx,dy,dt = r.get_deltas()

    #         print("Delta X: " + str(dx))
    #         print("Delta Y: " + str(dy))
    #         print("Delta Theta: " + str(dt))

    #         state += 1

    #     elif(state == 5):
    #         #We are now waiting to start the next section of the test
    #         #Do nothing until a user tells it to
    #         s_in = input()
    #         if(s_in == "stop"):
    #             state = -2
    #         state += 1

    #     elif(state == 6):
    #         #First Straight Away
    #         #Line follow until we hit a right turn
    #         while(get_curr_error() > -100):
    #             follow_lane = True

    #         follow_lane = False
    #         state += 1

    #     elif(state == 7):
    #         #The turn itself (rigt)
    #         #Use the pd controller to navigate the robot around the turn
    #         r.activate_motors(1.35, 1.0)
    #         time.sleep(1.0)
    #         r.activate_motors(0, 0)
    #         state += 1

    #     elif(state == 8):
    #         #The second straight away
    #         #Use line following until we see the red
    #         state = 3

    #     elif(state == 9):
    #         #We are on the red
    #         #Line follow until we no longer see then red
    #         #Use pd to drive a few inches forward then print  x,y,theta
    #         state = 4

    #     else:
    #         running = False
    
    r.stop()
    
__main__()