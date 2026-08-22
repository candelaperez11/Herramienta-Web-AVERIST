from . import abstraction_functions as absf
import ppl_functions as pplf
from ppl.polyhedron import NNC_Polyhedron
import networkx as nx
import optimization as opt
#import sys




#----------------------------------------------------------------------------------------------#
def constraint_system_to_set_string_old(constraints):
	
	""" Defines a string of ordered constraints transformed into strings. """

	constraint_list = []
	for constraint in constraints:
		constraint_list.append(str(constraint))


	return str(set(constraint_list))



#----------------------------------------------------------------------------------------------#
def constraint_system_to_set_string(constraints):
	
	""" Defines a string of ordered constraints transformed into strings. """
	
	constraint_list = []
	for constraint in constraints:
		constraint_list.append(str(constraint))
	
	
	return str(sorted(constraint_list))



#----------------------------------------------------------------------------------------------#
def set_nodes(WG,G,E):
	
	""" Creation of the nodes for the weighted abstract graph. They correspond to location-element
		pairs. The location is in the graph G and the element is in E. """
			
	for node in G.nodes():

		invariant = G.nodes[node]['inv']
	
		for element in E:
		
			element_constraints = element.constraints()
			
			element_str = constraint_system_to_set_string(element_constraints)

			# check if the element is contained in the invariant
			if invariant.contains(element):
					
				node_tuple = (node,element_str)
				dim = element.affine_dimension()
				WG.add_node(node_tuple,dim=dim)
				
					
	return WG



#----------------------------------------------------------------------------------------------#
def set_edges_and_weights(WG,G,E,opt_solver):
	
	""" Creation of the edges in the weighted abstract graph. They correspond to the presence
    of an element execution between location-element pairs. The weight on an edge corresponds
    to an upper-bound on the scaling of the executions represented by the edges. """
	
	subgraph_time = 0
	optimization_time = 0
	
	""" Creation of all the subgraphs associated to elements. """
	SG_dict = dict()
	
	for element in E:
		
		element_SG,sg_time = absf.subgraph(G,element)
		subgraph_time = subgraph_time + sg_time
		
		""" The graph is stored in case of having nodes with no empty dynamics. """
		element_str = constraint_system_to_set_string(element.constraints())
		SG_dict[element_str] = element_SG
	

	""" Loop for edge construction. """
	for element in E:

		print('ELEMENT: ', element.constraints())


		str_element = constraint_system_to_set_string(element.constraints())
		
		""" We check only for elements which are not points. """
		dim_element = element.affine_dimension()
		SG = SG_dict[str_element]
		
		if (dim_element != 0) and (SG.nodes()):
			
			""" Construction of the subgraph associated to a graph G and an element. """
			#SG,sg_time = absf.subgraph(G,element)
			#SG = SG_dict[str(element.constraints())]
            
			# print('**************************************************************************************************')
			# print('element =',element.constraints())
			# print('**************************************************************************************************')
			# print('SG.nodes =\n',SG.nodes(data=True))
			# print('SG.edges =\n',SG.edges(data=True))
			# print('subgraph time =',sg_time)
			# G_line = '---------------------------------------------------------------------\n'
			# for n in SG.nodes():
			# 	G_line += str(n)+'\n'
			# 	G_line += '		inv = '+ str(SG.nodes[n]['inv'].constraints())+'\n'
			# 	G_line += '		dyn = '+ str(SG.nodes[n]['dyn'].constraints())+'\n'
			# 	if SG.nodes[n]['dyn'].is_empty(): print('dyn is an empty set')
			# for e in SG.edges():
			# 	G_line += str(e)+'\n'
			# 	G_line += '		guard = '+str(SG[e[0]][e[1]]['guard'].constraints())+'\n'
			# print(G_line)
			# print('*******************************************************************************')
			# print('*******************************************************************************')

			#subgraph_time = subgraph_time + sg_time

			""" Extraction of the strongly connected components of the subgraph associated with the element 
			and construction of a graph with such components. """
			
			# scc_list = list(nx.strongly_connected_component_subgraphs(SG))

			# 1. Get the components as sets of nodes
			scc_nodes_list = list(nx.strongly_connected_components(SG))
			# print('ELEMENT AFTER scc_nodes_list: ', element.constraints())

			# 2. Create the subgraphs for your manual loops (lines 130-132)
			scc_list = [SG.subgraph(c).copy() for c in scc_nodes_list]

			# print('scc_list =',scc_list)
			# print('scc_list nodes',)
			# for a in scc_list:
			# 	print('a =',a)
			# 	print('nodes =',a.nodes(data=True))


			# SCCG = nx.condensation(SG,scc_list)
			# 3. Use the list of node SETS for the condensation function
			SCCG = nx.condensation(SG, scc_nodes_list)		
			SCCG_nodes = SCCG.nodes()
			# print('ELEMENT AFTER condensation: ', element.constraints())
    
			# print('----------------------- SCCG graph ----------------------- BEFORE')
			# print('nodes =', SCCG.nodes(data=True))
			# print('edges =', SCCG.edges(data=True))
			# print('----------------------------------------------------------')

			""" Addition of the subgraph part associated to the strongly connected component to a node tag, named 
			int_graph. """
			for i in range(len(scc_list)):
				SCCG.nodes[i]['int_graph'] = scc_list[i]

			# print('----------------------- SCCG graph ----------------------- AFTER')
			# print('nodes =', SCCG.nodes(data=True))
			# for n in SCCG.nodes():
			# 	print('   ',n, ' :',SCCG.nodes[n]['int_graph'].nodes())
			# print('edges =', SCCG.edges(data=True))
			# print('----------------------------------------------------------')
				
			""" Iteration over pairs of nodes in the strongly connected components graph. """
			for C1 in SCCG_nodes:
				for C2 in SCCG_nodes:
					# print('ELEMENT BEFORE PHI REL REACH: ', element.constraints())
					phi_rel_list = pplf.relation_reach.phi_rel_reach(element,C1,C2,SCCG)
					# print('ELEMENT AFTER phi_rel_list: ', element.constraints())
					#print 'phi_rel_list dimensions =',[n.space_dimension() for n in phi_rel_list]
					#if not phi_rel_list: print 'phi_rel_list is EMPTY'
					# print('ELEMENT AFTER PHI REL REACH: ', element.constraints())

					if phi_rel_list:
						""" Computation of the adjacent elements of the choosen element. """
						ae_list = absf.adjacent_elements(E,element)
							
						""" Iteration over pairs of adjacent elements. """
						for ae1 in ae_list:
							for ae2 in ae_list:
								
								str_ae1 = constraint_system_to_set_string(ae1.constraints())
								str_ae2 = constraint_system_to_set_string(ae2.constraints())
								
								if not pplf.ppl_functions.is_zero(ae1) and not pplf.ppl_functions.is_zero(ae2):
									
									print('-------------------------------------------')
									print('    ae1 =', ae1.constraints())
									print('    ae2 =', ae2.constraints())
									print('-------------------------------------------')

								
									#print 'Calling to init_rel'
									init_rel = pplf.relation_reach.rel_reach(ae1,element,C1,SCCG)
									#print 'init_rel=',init_rel.constraints()
									#if init_rel.is_empty(): print 'init_rel is EMPTY'
									#print 'Calling to final_rel'

									final_rel = pplf.relation_reach.rel_reach(element,ae2,C2,SCCG)
									#print 'final_rel=',final_rel.constraints()
									#if final_rel.is_empty(): print 'final_rel is EMPTY'
										
									if (not init_rel.is_empty()) and not (final_rel.is_empty()):

										""" Obtains the maximum scaling for an execution starting at element ae1,
										evolving through element between the connected components C1 and C2, and
										ending at element ae2. """
										#print 'Calling to optimization_set'
										scaling,relpoly,opt_set_time = opt.optimization.optimization_set(init_rel,phi_rel_list,final_rel,opt_solver)
										optimization_time = optimization_time + opt_set_time

										""" List of locations in the connected component C1 such that contain one of the adjacent elements. """
										ae1_loc_list = absf.CC_node_inclusion(SCCG,ae1,C1)
										#print 'ae1_loc_list=',ae1_loc_list
										""" List of locations in the connected component C2 such that contain the other adjacent element. """
										ae2_loc_list = absf.CC_node_inclusion(SCCG,ae2,C2)
										#print 'ae2_loc_list=',ae2_loc_list
										""" List of locations in ae1_loc_list such that the adjacent element ae1 can enter C1 through them. """
										enter_loc_list = absf.performance_locs(ae1_loc_list,ae1,element,C1,SCCG)
										#print 'enter_loc_list=',enter_loc_list
										""" List of locations in ae2_loc_list such that the adjacent element ae2 can exit C2 through them. """
										exit_loc_list = absf.performance_locs(ae2_loc_list,element,ae2,C2,SCCG)
										#print 'exit_loc_list=',exit_loc_list
	#
	#									""" List of locations from we can reach some of the locations in enter location list going through
	#									the adjacent element ae1. """
	#									loc1_list = pplf.reach.pre_reach_loc(enter_loc_list,ae1_loc_list,C1,SCCG)
	#									print 'loc1_list=',loc1_list
	#									""" List of locations we can reach from some of the locations in exit location list going through
	#									the adjacent element ae2. """
	#									loc2_list = pplf.reach.post_reach_loc(exit_loc_list,ae2_loc_list,C2,SCCG)
	#									print 'loc2_list=',loc2_list
										
										""" List of locations from we can reach some of the locations in enter location list going through
											the adjacent element ae1. """
										ae1_SG = SG_dict[constraint_system_to_set_string(ae1.constraints())]
										#print 'enter loc list =',enter_loc_list
										#print 'ae1 =',ae1
										#print 'ae1_SG =',ae1_SG.nodes(data=True)
										loc1_list = pplf.reach.pre_reach_loc_v2(enter_loc_list,ae1,ae1_SG)
										#print 'loc1_list=',loc1_list
										""" List of locations we can reach from some of the locations in exit location list going through
											the adjacent element ae2. """
										ae2_SG = SG_dict[constraint_system_to_set_string(ae2.constraints())]
										#print 'ae2_SG =',ae2_SG.nodes(data=True)
										loc2_list = pplf.reach.post_reach_loc_v2(exit_loc_list,ae2,ae2_SG)
										#print 'loc2_list=',loc2_list


										""" Iteration over pairs of locations on the last lists. """
										for q1 in loc1_list:
											for q2 in loc2_list:

												""" If there is no edge from (ae1,q1) to (ae2,q2) in the weighted abstract graph, it is tagged 
												with the scaling value and the weight is set to the scaling value. In case there exist such edge 
												it is tagged with the new scaling value and the weight is the maximum of the tagged values. """

												wg_node1 = (q1,str_ae1)
												wg_node2 = (q2,str_ae2)
#												print 'wg_node1 =',wg_node1
#												print 'wg_node2 =',wg_node2

												if WG.has_edge(wg_node1,wg_node2):
													
													weight = WG.edges[wg_node1, wg_node2]['weight']
													if scaling > weight:
														WG.edges[wg_node1, wg_node2]['weight'] = scaling
														WG.edges[wg_node1, wg_node2]['element'] = element
														WG.edges[wg_node1, wg_node2]['relation'] = relpoly

												else:

													if scaling > -1:
														WG.add_edge(wg_node1,wg_node2,weight=scaling,element=element,relation=relpoly)
				

	return WG,subgraph_time,optimization_time



#----------------------------------------------------------------------------------------------#
def construct_weighted_graph(G,E,opt_solver):

	""" Construction of the abstract weighted graph, given an input automaton and a set of
	elements determining a partition of the state space. """

	WG = nx.DiGraph()
	WG = set_nodes(WG,G,E)

	WG,subgraph_time,optimization_time = set_edges_and_weights(WG,G,E,opt_solver)

	return WG,subgraph_time,optimization_time


