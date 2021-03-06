import sys
from robot import Robot
import time
from Parsing.Parse import parseJsonAndReturnMap
import math

"""
This file handles administrative tasks for having a robot navigate an arbitrary roadway.
It loads the map, initializes the robot, and passes user commands to the robot


Concerns / other notes:
 -changing speeds mid-action:
  >right now, there are single actions (lane follow) which need to change speed based on where on the map the robot is
  >how can these speed changes be performed?
  >should be strongly tied to the map and map json
  >for each action, associate a speed
  >but then for lane following, how do we know how long to lane follow for until the speed changes?
  >need a distance associated with lane following
  >create LaneFollowForDistance
 -In actions executed via odometry by the arduino, where should the thread of control go?
  >arduino:
   -pi relinquishes control to arduino; writes the "go" command and then waits for arduino to respond with "done"
  >pi:
   -pi retains control. pi always tells arduino how to set the motors
   -pi relies on arduino's odometry to inform its decisions
   -basically, it would be a loop where the pi keeps checking with the arduino to see how much distance is covered
  >How does this work with ping & automatic speed regulation?
   -speed should always be ~speed limit unless there is another car ahead going slower
   -then ping will detect car and indicate we slow down
   -vision:
    >pi control: (current)
     -just adjust vref
    >arduino control:
     -vref adjusted on arduino
     -pi keeps sending corrections to arduino instead of full vref += delta_v
   -others:
    >pi control:
     -while checking translation, also checks ping
     -it calculates an adjustment based on ping
     -it updates its own vref and then informs arduino
     -requires synchronized vref; bleh
    >arduino control:
     -arduino calculates adjustment etc...
  >Conclusion: arduino control!!!
 -Stopping:
  >we can't always stop upon seeing red
  >instead, should "stop" at each state, then wait until next action is safe:
   -this will usually not stop at all: it will "stop" for so little time, it is imperceptible
   -when there are stopping conditions, it will actually stop
   -there are some states where a "real" stop is required regardless of whether there are hazards; how to handle this?
    >if action is four way intersection, wait
 -Odometry uses:
  >need odometry [x,y,theta] for termination events
  >we can associate an [x,y,theta] to each state, then update our odometry every time we hit a new state
  >so just use vision (stop sign detection) to determine when we have hit a new state (also for stop light stuff)
 -there will be stop signs at all sides of any intersection
 -the bottom intersection will be removed in favor of a straightaway
 -going past a t-intersection; our vision will fail
Commands to the robot:

shutdown:
  stops the robot and ends the program
  
reset [loc=None]:
  stops the robot, clears the command queue, and optionally resets the current location-node to "loc"
  
pause:
  pauses the robot; the robot stops driving and stays still until the 'resume' command is given
  
resume:
  starts the robot's execution. the robot will resume driving where it left off
  
load [map]:
  loads a map from a json file by filename
  
add [from=None] [to]:
  adds a command to the command queue
  commands take the form (from-location, to-location), and direct the robot to navigate from the "from" location to the "to" location
  if "from" is blank or invalid, the current state at the time of command execution is used as the start state
  if the start state is None and unspecified by the command, the robot does nothing and indicates failure
"""

port_ext = "ACM0"
mapname = "Parsing/map.json"

def get_commandline_args():
    global port_ext, mapname
    
    num_args = len(sys.argv)
    for i in range(num_args):
        if sys.argv[i] == "-p":
            if i+1 < num_args:
                port_ext = sys.argv[i+1]
            else:
                print("no value provided for -p; using default ACM0 instead")
        elif sys.argv[i] == "-m":
            if i+1 < num_args:
                mapname = sys.argv[i+1]
            else:
                print("no value provided for -m; using default 'map.json' instead")
    return (port_ext, mapname)

def load_map(mapname):
    return parseJsonAndReturnMap(mapname)
    
def __main__():
    port_ext, mapname = get_commandline_args()
    
    port = "/dev/tty" + port_ext
    print("loading map...")
    nmap = load_map(mapname)
    print("map was loaded")
    
    print("creating robot...")
    robot = Robot(nmap, port)
    print("robot was created")
    run_program = True
    try:
        while run_program:
            print("Waiting for command...")
            command = input().split(" ")
            if len(command) == 0:
                break
            # stop
            if command[0] == "shutdown":
                robot.shutdown()
                run_program = False
            # reset
            elif command[0] == "reset":
                loc = None if len(command) == 1 else command[1]
                robot.reset(loc)
            # pause
            elif command[0] == "pause":
                loc = None if len(command) == 1 else command[1]
                robot.pause(loc)
            # resume
            elif command[0] == "resume":
                robot.resume()
            # load
            elif command[0] == "load":
                if len(command) == 2:
                    nmap = load_map(command[1])
                    if nmap == None:
                        print("Could not find map named {}".format(command[1]))
                    else:
                        robot.load_map(nmap)
                else:
                    print("Exactly one argument, the map filename, is expected.")
            # add
            elif command[0] == "add":
                start = None
                end = None
                if len(command) == 3:
                    robot.enqueue_directions(int(command[1]), int(command[2]))
                elif len(command) == 2:
                    robot.enqueue_directions(None, command[1])
                else:
                    print("Exactly one argument, the map filename, is expected.")
            elif command[0] == "addall":
                start = None
                end = None
                if len(command) >= 3:
                    lst = list(map(lambda x : int(x), command[1:]))
                    robot.enqueue_all_directions(lst)
                else:
                    print("Exactly one argument, the map filename, is expected.")
                print("Done")
            elif command[0] == "addallskip":
                start = None
                end = None
                if len(command) >= 4:
                    lst = list(map(lambda x : int(x), command[2:]))
                    robot.enqueue_all_directions(lst, int(command[1]))
                else:
                    print("Exactly one argument, the map filename, is expected.")
                print("Done")
            elif command[0] == "lighttest":
                print("drive to a stop sign")
                robot.lane_follow(.1, "intersection")
                print("saw stop sign")
                if (not robot.action_is_safe(0)):
                    robot.stop()
                    print("wait for the action to be safe...")
                    while (not robot.action_is_safe(0)):
                        print("...")
                        time.sleep(.05)
                print("action is safe! resume driving!")
                robot.drive_straight(.12)
                robot.stop()
            elif command[0] == "laneturn":
                print("run lane follow heading-based state change. Press enter to begin")
                while input() != "q":
                    print("lane follow...")
                    robot.set_heading(float(command[1])*math.pi)
                    print("updated heading. now lane follow")
                    robot.lane_follow(command[2], "loc", float(command[2])*math.pi)
                    robot.stop()
                    print("press enter to rerun or q to quit")
            elif command[0] == "test":
                if len(command) > 1:
                    robot.set_heading(float(command[1])*math.pi)
                print(robot._get_heading())
            elif command[0] == "lanefollow":
                while input() != "q":
                    robot.lane_follow(command[1], "intersection")
                robot.stop()
            elif command[0] == "left":
                while input() != 'q':
                    robot.make_left_turn(.108)
                    robot.stop()
            elif command[0] == "right":
                while input() != 'q':
                    robot.make_right_turn(.108)
                    robot.stop()
            else:
                print("Command not recognized")
    except Exception as e:
        print(e)
        robot.active = False
        robot.stop()
        robot.vision_thread.join()
        robot.fsm_thread.join()
            
__main__()