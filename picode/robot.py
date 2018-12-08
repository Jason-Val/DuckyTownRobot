class Robot:
    def __init__(self, map, port="/dev/ttyACM0"):
        self.s = serial.Serial(port,115200,timeout=1)
        self.paused = False
        self.vref = 1.08
        self.fsm = finite_state_machine(self, map)
        self.active = True
        
        # threads for vision etc
        self.vision_thread = threading.Thread(target=vision.start_thread, name="vision_thread")
        self.fsm_thread = threading.Thread(target=fsm.fsm_loop, name="fsm_thread")
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
        pass
        
    def stop(self):
        pass
        
    def reset(new_state):
        pass
    
    def load_map(map):
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
        
    def lane_follow(self, distance=0):
        follow_lane = True
        start_trans = self._get_translation()
        
        while (follow_lane):
            if not paused:
                error = vision.get_error()
                if(error == None):
                    continue
                error += self.error_offset #TODO: move this to the vision module
                delta_error = error - self.prev_error
                self.prev_error = error
                
                delta_v = -self.K*error -self.B*delta_error
                
                self._send_to_arduino("4 {}".format(delta_v/2))
                
                #self._activate_motors(self.vref + delta_v/2, self.vref - delta_v/2)
                
                follow_lane = not vision.saw_stop_sign()
                if distance > 0 and self._get_translation() - start_trans > distance:
                    follow_lane = False
                time.sleep(0.05)
            else:
                time.sleep(0.5)
        self._activate_motors(0, 0)
        
    """
    These commands write to arduino to execute the desired action, then wait until the action is completed
    In the case of turning, this will be when the desired distance is covered
    """
    def make_left_turn(self, velocity):
        self._send_to_arduino("1 {0};".format(velocity))
        cmd = self.s.read_until()
        
    def make_right_turn(self, velocity):
        self._send_to_arduino("2 {0};".format(velocity))
        cmd = self.s.read_until()
        
    def drive_straight(self, velocity):
        self._send_to_arduino("0 {0};".format(velocity))
        cmd = self.s.read_until()
        
    def action_is_safe(action):
        #use ping, vision, etc to determine whether action is safe
        pass
        
    # TODO: implement this on the arduino side. Also, consider possibility of reading the wrong command
    def _get_translation(self):
        self._send_to_arduino("2")
        cmd, trans = self.s.read_until().split()
        return float(trans)
        
    def _activate_motors(self, v_l, v_r):
        self._send_to_arduino("5 {0} {1};".format(format(v_l, '.4f'), format(v_r, '.4f')))
        
    def _send_to_arduino(self, cmd):
        self.serial_sem.acquire()
        self.s.write(cmd.encode('utf-8'))
        self.s.flush()
        self.serial_sem.release()