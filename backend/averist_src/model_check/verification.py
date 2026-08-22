from . import graph_functions as gf

#----------------------------------------------------------------------------------------------#
def verification(WG):
	
	""" Given an abstract weighted graph, a search for cycles with weight greater than one is 
	performed. The non existence of any cycle with such feature implies the stability of the 
	input hybrid automaton. In case of existence, the cycle is returned. """
    
	neg_cycle = False
    
	if len(WG.edges()) == 0:
		message = 'There is no possible executions'
        
	else:
		
		neg_cycle, predecessor_list, distance_list, node_in_path_with_cycle = gf.greater_than_one_edge_cycle(WG)
		
		if neg_cycle:
			message = 'Abstract counterexample'
			cycle = gf.negative_cycle(predecessor_list, node_in_path_with_cycle)
		else:
			message = 'Stable'
	
	if not neg_cycle: cycle = []
    
	return message,cycle
