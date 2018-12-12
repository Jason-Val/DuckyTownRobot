import threading
import vision
import time
import serial
import math
from state_machine import FiniteStateMachine

class Robot:
    def __init__(self, map, port="/dev/ttyACM0"):
        self.s = serial.Serial(port,115200,timeout=6)
        self.paused = False
        self.fsm = FiniteStateMachine(self, map)
        self.active = True
        self.stopped = True
        self.fsm_active = False
        
        # threads for vision etc
        self.vision_thread = threading.Thread(target=vision.start_thread, name="vision_thread")
        self.fsm_thread = threading.Thread(target=self.fsm.fsm_loop, name="fsm_thread")
        self.serial_sem = threading.Semaphore()
        
        # visual pd constants
        scaleK = 5.40*1000
        scaleB = 4.85*1000
        self.error_offset = 5
        self.K = 1.0/scaleK
        self.B = 1.0/scaleB
        self.prev_error = 0.0
        
        self.vision_thread.start()
        self.fsm_thread.start()
        
        # wait for serial communications to begin
        time.sleep(2)
        # wait
        while(vision.img == None):
            time.sleep(0.1)
        
    def shutdown(self):
        self.stop()
        self.active = False
        time.sleep(1)
        self.s.close()
        
    def stop(self):
        self.stopped = True
        self._send_to_arduino("5 0;".format())
        
    def reset(self, new_state):
        pass
    
    def load_map(self, map):
        reset(None)
        self.fsm.map = map
        
    def pause(self):
        self.paused = True
        time.sleep(.5) # give things a chance to stop
        self._activate_motors(0,0)
        
    def resume(self):
        self.paused = False
        
    def enqueue_directions(self, start_location, end_location):
        self.fsm_active = True
        return self.fsm.enqueue_directions(start_location, end_location)
        
    # TODO: fine-tune this
    def _is_turning(self, vision_error):
        return vision_error > 200
        
    def lane_follow(self, velocity, stopping_condition, location=0):
        follow_lane = True
        print(format(float(velocity), '.4f'))
        self._send_to_arduino("4 {};".format( format(float(velocity), '.4f') ))
        time.sleep(0.5)
        print("Begin lane following")
        heading_epsilon = 2*math.pi/64
        
        slow_speed = 0.108
        notified_slow = False
        
        t = time.time()
        
        stop_sign_seen = False
        while (follow_lane):
            if not self.paused:
                error = vision.get_error()
                #print("got error...")
                if(error == None):
                    continue
                error += self.error_offset #TODO: move this to the vision module
                if (not notified_slow and error > 200):
                    notified_slow = True
                    self._send_to_arduino("4 {};".format( format(float(slow_speed), '.4f') ))
                elif (notified_slow and not error > 200):
                    notified_slow = False
                    self._send_to_arduino("4 {};".format( format(float(velocity), '.4f') ))
                delta_error = error - self.prev_error
                self.prev_error = error
                
                delta_v = -self.K*error -self.B*delta_error
                self._send_to_arduino("3 {};".format(format(delta_v/2), '.4f'))
                #print(delta_error)
                if stopping_condition == "intersection":
                    follow_lane = not ( time.time() - t > 1 and vision.isStopSign() >= 0.0)
                    """
                    if(not stop_sign_seen):
                        #Update if we have seen the stop sign
                        if(vision.isStopSign() > 0.0):
                            stop_sign_seen = True
                    else:
                        #Keep driving until it is where we want it to be
                        if(vision.isStopSign() > vision.y_max - 400):
                            follow_lane = False
                    """
                if stopping_condition == "loc":
                    follow_lane = True
                    #actual_heading = self._get_heading()
                    #print("actual heading: {}".format(actual_heading))
                    #follow_lane =  abs((actual_heading % 2*math.pi) - location) > heading_epsilon:
                    
                time.sleep(0.05)
            else:
                time.sleep(0.5)
        print("detected state change")
        
        
    """
    These commands write to arduino to execute the desired action, then wait until the action is completed
    In the case of turning, this will be when the desired distance is covered
    """
    def drive_straight(self, velocity):
        self._send_action_to_arduino(0, velocity)
    
    def make_left_turn(self, velocity):
        self._send_action_to_arduino(1, velocity)
        
    def make_right_turn(self, velocity):
        self._send_action_to_arduino(2, velocity)
        
    def action_is_safe(self, action):
        #use ping, vision, etc to determine whether action is safe
        #print("Saw a green light: {}".format(vision.saw_green_light()))
        #print("returning ")
        return (not vision.isStopSign() >= 0) or vision.saw_green_light()
        #return vision.saw_green_light()
    
    """
    # TODO: implement this on the arduino side. Also, consider possibility of reading the wrong command
    def _get_translation(self):
        self._send_to_arduino("2")
        cmd, trans = self.s.read_until().split()
        return float(trans)
    """
    def _get_heading(self):
        self._send_to_arduino("6")
        response = self.s.read_until()
        print(response)
        return float(response.decode('utf-8'))
    
    def _send_action_to_arduino(self, action, velocity):
        self._send_to_arduino("{0} {1};".format(action, format(float(velocity), '.4f')))
        cmd = ''
        t = time.time()
        while cmd != b'1\r\n':
            cmd = self.s.read_until()
            if time.time() - t > 10:
                print("timed out")
                break
    
    def _activate_motors(self, v_l, v_r):
        self._send_to_arduino("5 {0} {1};".format(format(float(v_l), '.4f'), format(float(v_r), '.4f')))
        
    def _send_to_arduino(self, cmd):
        #self.serial_sem.acquire()
        self.s.write(cmd.encode('utf-8'))
        self.s.flush()
        #self.serial_sem.release()