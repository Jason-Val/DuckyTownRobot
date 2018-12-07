class NodeMap:
	nodes = []

	def __init__(self, nds):
		self.nodes = nds

	def getNodeFromNumber(self, num):
		for n in self.nodes:
			if(num == n.location):
				return n
		print("Error in Getting Node From Number: {}".format(num))
		return None

	def getStatesQueue(self, start_loc, end_loc):
		#Reset All Parents
		#Reset All Weights
		for n in self.nodes:
			n.parent_node = None
			n.total_weight = 99999999999999

		#List Of the Visited Node's NUMBERS
		visited = []
		#List of Unvisted Nodes THEMSELVES
		unvisited = []

		unvisited = self.nodes.copy()

		curr_node = self.getNodeFromNumber(start_loc)
		end_node = self.getNodeFromNumber(end_loc)
		curr_node.total_weight = 0

		running = True
		while(running):

			for i in range(len(curr_node.children)):
				child_num = curr_node.children[i]
				child_weight = curr_node.children_weights[i]

				if(child_num in visited):
					continue
				else:
					child_node = self.getNodeFromNumber(child_num)
					if(curr_node.total_weight + child_weight < child_node.total_weight):
						child_node.total_weight = curr_node.total_weight + child_weight
						child_node.parent_node = curr_node
			
			unvisited.remove(curr_node)
			visited.append(curr_node.location)

			#End Conditions

			if(curr_node.location == end_node.location):
				running = False
				continue
			#Make sure it is still possible to reach the destination
			cnt = 0
			for nd in unvisited:
				if(nd.total_weight < 99999999999999):
					cnt = cnt + 1
			if(cnt <= 0):
				print("Impossible to Reach the Destination")
				running = False
				continue 

			#Set curr_node
			curr_node = unvisited[0]
			for nd in unvisited:
				if(nd.total_weight < curr_node.total_weight):
					curr_node = nd

		lst = []
		if(curr_node.location == end_node.location):
			#Backtrack to make list of states
			while(not curr_node == None):
				lst.insert(0, curr_node)
				curr_node = curr_node.parent_node

		print(lst)

		ret_lst = []
		for n_index in range(len(lst)-1):
			n = lst[n_index]
			p = lst[n_index+1]
			elem = (n.children_actions[n.children.index(p.location)], p.location)
			ret_lst.append(elem)

		return ret_lst
