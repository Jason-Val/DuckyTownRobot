class Node:
	#Attributes
	location = -1
	children = []
	children_weights = []
	children_actions = []
	children_action_speeds = []
    children_action_locations = []

	#Used in Djikstras
	parent_node = None
	total_weight = 99999999999999

	def __init__(self, loc, childrn, childrn_weights, childrn_actions, childrn_action_speeds, childrn_action_locations):
		self.location = loc
		self.children = childrn
		self.children_weights = childrn_weights
		self.children_actions = childrn_actions
		self.children_action_speeds = childrn_action_speeds
        self.children_action_locations = childrn_action_locations

	def reset(self):
		self.parent_node = None
		self.total_weight = 99999999999999

	def __str__(self):
		return str(self.location)

	def __repr__(self):
		return str(self.location)

	def print(self):
		print("Location: " + str(self.location))
		print("Children: " + str(self.children))
		print("Children Weights: " + str(self.children_weights))
		print("Children Actions: " + str(self.children_actions))
		print("Children Action Speeds: " + str(self.children_action_speeds))
        print("Children Action Locations: " + str(self.childrn_action_locations))
		print("Parent: " + str(self.parent_node))
		print("Total Weight: " + str(self.total_weight))
		print()