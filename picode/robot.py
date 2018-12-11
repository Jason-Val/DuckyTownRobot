import threading
import vision
import time
import serial
from state_machine import FiniteStateMachine

class Robot:
    def __init__(self, map, port="/dev/ttyACM0"):
        self.s = serial.Serial(port,115200,timeout=6)
        self.paused = False
        self.fsm = FiniteStateMachine(self, map)
        self.active = True
        self.stopped = True
        
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
        return self.fsm.enqueue_directions(start_location, end_location)
        
    # TODO: fine-tune this
    def _is_turning(self, vision_error):
        return vision_error > 350
        
    def lane_follow(self, velocity, stopping_condition):
        follow_lane = True
        self._send_to_arduino("5 {};".format( format(velocity, '.4f') ))
        
        print("Begin lane following")
        
        while (follow_lane):
            if not self.paused:
                error = vision.get_error()
                if(error == None):
                    continue
                error += self.error_offset #TODO: move this to the vision module
                delta_error = error - self.prev_error
                self.prev_error = error
                
                delta_v = -self.K*error -self.B*delta_error
                print(format(delta_v/2, '.4f'))
                self._send_action_to_arduino(3, delta_v/2)
                #self._send_to_arduino("3 {};".format(format(delta_v/2), '.4f'))
                
                if stopping_condition == "intersection":
                    follow_lane = vision.isStopSign() < 0.0
                    print(vision.isStopSign())
                    print(follow_lane)
                if stopping_condition == "turn":
                    follow_lane = not self._is_turning(error)
                if stopping_condition == "straight":
                    follow_lane = self._is_turning(error)

                time.sleep(0.05)
            else:
                time.sleep(0.5)
        
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
        return not (vision.isStopSign() >= 0 and not vision.saw_green_light())
    
    """
    # TODO: implement this on the arduino side. Also, consider possibility of reading the wrong command
    def _get_translation(self):
        self._send_to_arduino("2")
        cmd, trans = self.s.read_until().split()
        return float(trans)
    """
    
    def _send_action_to_arduino(self, action, velocity):
        self._send_to_arduino("{0} {1};".format(action, format(velocity, '.4f')))
        cmd = ''
        while cmd != '1':
            cmd = self.s.read_until()
    
    def _activate_motors(self, v_l, v_r):
        self._send_to_arduino("5 {0} {1};".format(format(v_l, '.4f'), format(v_r, '.4f')))
        
    def _send_to_arduino(self, cmd):
        self.serial_sem.acquire()
        self.s.write(cmd.encode('utf-8'))
        self.s.flush()
        self.serial_sem.release()