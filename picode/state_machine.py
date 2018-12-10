import time
from Parsing.Node import Node
from Parsing.NodeMap import NodeMap
    
class finite_state_machine:
    def __init__(self, robot, map):
        self.robot = robot
        self.map = map
        self.current_state = None
        self.command_queue = []
        
    def fsm_loop(self):
        while (robot.active):
            if (not robot.paused):
                next_state, actions = self.get_next_state_and_actions()
                if next_state == None:
                    self.robot.stop() 
                    continue
                if next_state == self.current_state:
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
        
    def get_next_state_and_actions():
        next_state = [None, None]
        if len(self.command_queue) > 0:
            next_state = self.command_queue[0]
            self.command_queue = self.command_queue[1:]
        return next_state
       
    def enqueue_directions(self, start_state, end_state):
        if start_state == None:
            start_state = self.current_state
        directions = self.map.getStatesQueue(start_state, end_state)
        if directions == None or len(directions) == 0:
            print("Enqueuing new directions failed")
            return
        self.command_queue = self.command_queue + directions
    
    def make_action(self, action):
        if action[0] == "LaneFollowToStop":
            robot.lane_follow(action[1], "intersection")
        elif action[0] == "LaneFollowToTurn":
            robot.lane_follow(action[1], "turn")
        elif action[0] == "LaneFollowToStraight":
            robot.lane_follow(action[1], "straight")
        elif "Left" in action[0]:
            robot.make_left_turn(action[1])
        elif "Right" in action[0]:
            robot.make_right_turn(action[1])
        elif "Straight" in action[0]:
            robot.drive_straight(action[1])