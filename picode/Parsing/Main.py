import sys
from Parse import parseJsonAndReturnMap
from Node import Node
from NodeMap import NodeMap

def getNode(name, size):
	num = int(input("Enter Robot {}: ".format(name)))
	while(num < 0 or num >= size):
		print("Invalid {}".format(name))
		print("Enter Value from 0-{}".format(size-1))
		num = int(input("Enter Robot {}: ".format(name)))
	return num

node_map = parseJsonAndReturnMap()
if(node_map == None):
	sys.exit()

location = getNode("Location", len(node_map.nodes))
destination = getNode("Destination", len(node_map.nodes))

q = node_map.getStatesQueue(location, destination)

while(True):
	print("Queue Nodes:")
	for qt in q:
		print(qt)
		acts = qt[0]
		nxt_node = qt[1]
		location = nxt_node
	destination = getNode("Destination", len(node_map.nodes))
	print()
	q = node_map.getStatesQueue(location, destination)