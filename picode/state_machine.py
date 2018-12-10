import time

actions = ("lane follow",
           "straight four way",
           "left turn four way",
           "right turn four way",
           "left intersection",
           "right intersection",
           "left four way",
           "right four way")
    
class finite_state_machine:
    def __init__(self, robot, map):
        self.robot = robot
        self.path_planner = Path_planner()
        self.map = map
        self.current_state = None
        self.command_queue = []
        
    def fsm_loop(self):
        while (robot.active):
            if (not robot.paused):
                next_state = self.get_next_state()
                if next_state == None:
                    self.robot.stop() 
                    continue
                if next_state == self.current_state:
                    continue
                actions = self.get_action(self.current_state, next_state)
                if len(actions) == 0:
                    print("The next set of directions starts at state {}.\
                           Please move me there and then press 'ENTER'".format(next_state))
                    self.robot.pause()
                    input()
                    self.robot.resume()
                    continue
                for action in actions:
                    if not robot.action_is_safe(action[0]):
                        robot.stop()
                    while not robot.action_is_safe(action[0]):
                        time.sleep(0.05)
                    self.make_action(action)    # blocks until action is complete
                self.current_state = next_state
                #robot.update_state()        # uses current state to update x,y,theta of robot
            else:
                time.sleep(0.5)
        
    def get_next_state():
        next_state = None
        if len(self.command_queue) > 0:
            next_state = self.command_queue[0]
            self.command_queue = self.command_queue[1:]
        return next_state
       
    def enqueue_directions(self, start_state, end_state):
        if start_state == None:
            start_state = self.current_state
        directions = self.path_planner.get_directions(start_state, end_state, map)
        if directions == None or len(directions) == 0:
            print("Enqueuing new directions failed")
            return
        self.command_queue = self.command_queue + directions
        
    def get_action(self, current_state, next_state):
        #get this value from parsed json file
        pass
    
    def make_action(self, action):
        if action[0] == "lane_follow":
            robot.lane_follow(action[1])
        elif "left" in action[0]:
            robot.make_left_turn(action[1])
        elif "right" in action[0]:
            robot.make_right_turn(action[1])
        elif "straight" in action[0]:
            robot.drive_straight(action[1])