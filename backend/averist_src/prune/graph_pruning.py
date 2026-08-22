from ppl import *
import networkx as nx

#----------------------------------------------------------------------------------------------#
def delete_selfloops(G):
	
	""" Delete self edges when there are no greater dimensional elements entering to
		and outgoing from the element which contains the self loop. """
	
	# selfloops = G.selfloop_edges(data=True)
	# Usamos la función del módulo networkx (importado como nx)
	selfloops = list(nx.selfloop_edges(G, data=True))	# NetworkX v3
	
	
	for sl in selfloops:
		
		str_element_through = str(sl[2]['element'].constraints())
		element_through = sl[2]['element']
		et_dim = element_through.affine_dimension()
		node = sl[0]
		
		edges_in_node = G.in_edges(node,data=True)
		edges_out_node = G.out_edges(node,data=True)
	
		
		# Delete edges which are selfloops
		edges_finishing_at_node = []
		for ein in edges_in_node:
			if ein[0] != ein[1]:
				edges_finishing_at_node.append(ein)
		
		edges_starting_at_node = []
		for eout in edges_out_node:
			if eout[0] != eout[1]:
				edges_starting_at_node.append(eout)

#		print('edges in =',edges_in_node)
#		print('----------------------------------------------------------------------')
#		print('edges finishing =',edges_finishing_at_node)
#		print('----------------------------------------------------------------------\n')
#		print('edges out =',edges_out_node)
#		print('----------------------------------------------------------------------')
#		print('edges starting =',edges_starting_at_node)
#		print('----------------------------------------------------------------------\n')

		# Check conditions to delete the self loop
		# condition 1: the element the self loop goes through, is the same as the element in the node
		c1 = (node[1] == str_element_through)
			
		if c1:
			
			greater_entry_element = False
			greater_outer_element = False
			
			for ef in edges_finishing_at_node:
				#print('ef[0]=',ef[0])
				#print('G.nodes[ef[0]]=',G.nodes[ef[0]])
				ef_through_poly = ef[2]['element']
				ef_dim = ef_through_poly.affine_dimension()
				# condition 2: the entering element through has less dimension than the node element
				#ef_dim = G.nodes[ef[0]]['dim']
				if ef_dim > et_dim: greater_entry_element = True

			for es in edges_starting_at_node:
				# condition 3: the outgoing element through has less dimension than the node element
				es_through_poly = es[2]['element']
				es_dim = es_through_poly.affine_dimension()
				if es_dim > et_dim: greater_outer_element = True

			if (not greater_entry_element) or (not greater_outer_element):
				G.remove_edge(node,node)
	
	return G



#----------------------------------------------------------------------------------------------#
def delete_duplicate_edges(G):

	""" In case of having (e1) --e--> (e) --e--> (e2) and also (e1) --e--> (e2) with (e) not 
		having anymore entering or outgoing edges, we delete the node (e). """

	for node in G.nodes(data=True):	# Possible error in the future: En Python 3,
	# G.nodes(data=True) devuelve una vista (view) dinámica, no una lista estática.
	# Si eliminas un nodo (G.remove_node) mientras estás iterando sobre esa misma vista,
	# Python lanzará un: RuntimeError: dictionary changed size during iteration
		
		str_element_node = node[0][1]
		
		loc_node = node[0]
		edges_in = G.in_edges(loc_node,data=True)
		edges_out = G.out_edges(loc_node,data=True)

		#print('len(edges_in) =', len(edges_in))
		#print('len(edges_out) =', len(edges_out))
		
		for ei in edges_in:
			
			e1 = ei[0][1]
			str_ei_through = str(ei[2]['element'].constraints())
			#print('e1=',e1)
			#print('ei through =',str_ei_through)

			for eo in edges_out:
				
				e2 = eo[1][1]
				str_eo_through = str(eo[2]['element'].constraints())
				#print('e2=',e2)
				#print('eo through =',str_eo_through)

				edge_data = G.get_edge_data(ei[0],eo[1])
				#print('edge_data =',edge_data)
				if edge_data != None:
					str_edge_element = str(edge_data['element'].constraints())
					#print('str_edge_element =', str_edge_element)
					if (str_ei_through == str_element_node) and (str_eo_through == str_element_node) and (str_edge_element == str_element_node) and (len(edges_in) == 1) and (len(edges_out) == 1):
						print('We remove the node')
						G.remove_node(loc_node)


	return G






