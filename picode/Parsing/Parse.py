import json
from Parsing.Node import Node
from Parsing.NodeMap import NodeMap

# def sampleLaneFollow():
# 	print("Lane Following")
# def sampleStop():
# 	print("Stopping")
# def sampleTurnLeft():
# 	print("Turning Left")
# def sampleTurnRight():
# 	print("Turning Right")

# def sampleStopCond():
# 	print("Detecting Stop")
# 	return True
# def sampleWaitCond():
# 	print("Waiting")
# 	return True

# allowed_actions = {
# 	"" : None,
# 	"LaneFollow" : sampleLaneFollow,
# 	"Stop" : sampleStop,
# 	"TurnLeft" : sampleTurnLeft,
# 	"TurnRight" : sampleTurnRight
# }

# allowed_stop_conds = {
# 	"" : None,
# 	"StopSign" : sampleStopCond,
# 	"Wait" : sampleWaitCond
# }

allowed_actions = ["", "LaneFollow", "Stop", "TurnLeft", "TurnRight"]
allowed_stop_conds = ["", "StopSign", "Wait"]

def validateData(location, children, weights, actions, speeds, num_nodes):
	return True
	# if(location < 0 or location >= num_nodes):
	# 	return False

	# num_children = len(children)
	# if(not (num_children == len(weights) and num_children == len(actions) and num_children == len(stop_conditions) and num_children == len(speeds) and num_children < num_nodes)):
	# 	print("Error in JSON Node {}: Number of child features!".format(location))
	# 	return False
	# for w in weights:
	# 	if(w < 0 ):
	# 		print("W")
	# if()

def parseJsonAndReturnMap(name = 'map.json'):
	print("Reading JSON")
	obj = None
	with open(name, 'r') as fp:
		obj = json.load(fp)

	print("Building Map and Validating JSON")

	node_list = []
	for thing in obj:
		location = thing["location"]
		children = thing["children"]
		weights = thing["weights"]
		actions = thing["actions"]
		speeds = thing["speeds"]

		valid = validateData(location, children, weights, actions, speeds, len(obj))
		if(not valid):
			return None

		n = Node(location, children, weights, actions, speeds)
		node_list.append(n)
	return NodeMap(node_list)

