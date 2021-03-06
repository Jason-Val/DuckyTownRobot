import time
import math
from Parsing.Node import Node
from Parsing.NodeMap import NodeMap
    
class FiniteStateMachine:
    def __init__(self, robot, mp):
        self.robot = robot
        self.map = mp
        self.current_state = None
        self.command_queue = []
        
    def fsm_loop(self):
        while (self.robot.active):
            if (self.robot.fsm_active):
                actions, next_state = self.get_next_state_and_actions()
                if self.robot.fsm_active and next_state == None:
                    self.robot.stop()
                    self.robot.fsm_active = False
                    print("Completed all directions!")
                    continue
                if next_state == self.current_state:
                    continue
                if (self.current_state == 11 or self.current_state == 7):
                    print("Update heading to down")
                    self.robot.set_heading(math.pi*3/2)
                if (self.current_state == 12):
                    print("Update heading to left")
                    self.robot.set_heading(0)
                if (self.current_state == 8):
                    print("Update heading to right")
                    self.robot.set_heading(math.pi)
                print("Current state is {0}. Next state is {1}".format(self.current_state, next_state))
                for action in actions:
                    print("Next action is {}".format(action[0]))
                    if not self.robot.action_is_safe(action[0]):
                        print("Action is not safe. Begin waiting...")
                        self.robot.stop()
                    while not self.robot.action_is_safe(action[0]):
                        time.sleep(0.05)
                    print("Make action {0} at velocity {1}".format(action[0], action[1]))
                    self.make_action(action)    # blocks until action is complete
                self.current_state = next_state
                #robot.update_state()        # uses current state to update x,y,theta of robot
            else:
                time.sleep(0.5)
        
    def get_next_state_and_actions(self):
        next_state = [None, None]
        if len(self.command_queue) > 0:
            next_state = self.command_queue[0]
            self.command_queue = self.command_queue[1:]
        return next_state
       
    def enqueue_directions(self, start_state, end_state):
        if start_state == None:
            start_state = self.current_state
        if self.current_state == None:
            self.current_state = start_state
        directions = self.map.getStatesQueue(start_state, end_state)
        if directions == None or len(directions) == 0:
            print("Enqueuing new directions failed")
            return
        self.command_queue = self.command_queue + directions
    
    def enqueue_all_directions(self, states, skip=0):
        if states[0] == None:
            states[0] = self.current_state
        if self.current_state == None:
            self.current_state = states[0]

        directions = []

        for i in range(len(states)-1):
            directions += self.map.getStatesQueue(states[i], states[i+1])

        print("Directions: ")
        print(directions)
        
        if directions == None or len(directions) == 0:
            return

        if (skip > 0):
            for i in range(skip):
                directions[0][0].pop(0)
                #Remove 2nd [0] if this doesn't work

        self.command_queue = self.command_queue + directions

    def make_action(self, action):
        if action[0] == "LaneFollowToStop":
            self.robot.lane_follow(action[1], "intersection")
        elif action[0] == "LaneFollowToLoc":
            self.robot.lane_follow(action[1], "loc", action[2])
        elif "Left" in action[0]:
            self.robot.make_left_turn(action[1])
        elif "Right" in action[0]:
            self.robot.make_right_turn(action[1])
        elif "Straight" in action[0]:
            self.robot.drive_straight(action[1])