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
                    self.robot.stop() #this may be unnecessary; the robot should only move under the influence of an action, and each action should relinquish control upon its completion
                    continue
                if next_state == self.current_state:
                    continue
                action = self.get_action(self.current_state, next_state)
                if action == None:
                    print("The next set of directions starts at state {}.\
                           Please move me there and then press 'ENTER'".format(next_state))
                    self.robot.pause()
                    input()
                    self.robot.resume()
                    continue
                while not robot.action_is_safe(action):
                    time.sleep(0.05)
                self.make_action(action)
                self.current_state = next_state
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
        if action == "lane_follow":
            robot.lane_follow()
        elif "left" in action:
            robot.make_left_turn()
        elif "right" in action:
            robot.make_right_turn()
        elif "straight" in action:
            robot.drive_straight()