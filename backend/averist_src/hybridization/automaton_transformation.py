import networkx as nx
import partition as p
import ppl_functions as pplf
import files as f
from ppl import *
from . import hybrid_functions as hf
from sage.modules.free_module_element import vector
from numpy import array,dot



#----------------------------------------------------------------------------------------------#
def const_to_poly_dyn(dyn,var_dict):

	""" The dynamics from a piecewise constant derivative hybrid automaton
	will be expressed as the dynamics of a polyhedral hybrid automaton.
	-----------------------------------------------------------------------
	input:	dyn			dx=a AND dy=b  or  dx+dy<=c
			var_dict	{'x':0,'y':1}
	output:	dyn_pg		x=a AND y=b or x+y<=c. """

	dyn_pg = dyn

	for var in var_dict:
		dvar = 'd' + var
		dyn_pg = dyn_pg.replace(dvar,var)

	return dyn_pg



#----------------------------------------------------------------------------------------------#
def LHA_to_PHA_maximal_norm(LG,LE,var_dict,inv_var_dict,namefolder,diameter_bound):
	
	""" A Linear Hybrid Automaton (LHA) expressed as a graph will be
		transformed into a Polyhedral Hybrid Automaton (PHA), by just
		considering the maximal elements, so the elements with affine 
		dimension equal to the space dimension.
		-----------------------------------------------------------------------
		input: 	LG		linear hybrid automaton graph
				LE		homogeneous predicate coefficients matrix	list of ppl.linear expressions
				folder	folder name for the files will be created
		output:	PG		polyhedral hybrid automaton graph
				E		elements. """
    

    
	output = namefolder + '/output'
	dim = len(var_dict)

#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		START	#
#***********************************************************************************************************#
	new_LE_coeffs = []
#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		END		#
#***********************************************************************************************************#

	PG = nx.DiGraph()

	auxx_E, creation_time = p.create_elements.create_elements(LE)
#	print('Element creation time = ', creation_time)
	
	# Just consider the maximal elements
	aux_E = []
	for auxx_e in auxx_E:
		if auxx_e.affine_dimension() == dim:
			cauxx_e = NNC_Polyhedron(auxx_e)
			cauxx_e.topological_closure_assign()
			aux_E.append(cauxx_e)
	
	mark_E = []
	
	# Systems of constraints defining the elements
	c_E = []
	for aux_e in aux_E:
		c_E.append(aux_e.constraints())
    
	ef_name = output +'/elements.dat'
	f.functions.list2file(c_E,ef_name)
    
	node_pg_rel_list = []
	node_rel_list = []
	number_node_lg = 0

#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		START	#
#***********************************************************************************************************#
	max_diameter = diameter_bound
#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		END		#
#***********************************************************************************************************#

	for node in LG:
		
		node_pg_list = []
		node_elem_list = []
		
		for element in aux_E:

			elem_aux = NNC_Polyhedron(element)

			elem_aux.topological_closure_assign()
			
			inv_poly = LG.nodes[node]['inv']
			
			# check if the element is contained in the invariant
			if inv_poly.contains(element):
                
				dyn = LG.nodes[node]['dyn']
				
				node_pg = 'loc'+str(number_node_lg)
				number_node_lg = number_node_lg + 1
                
				# check the intersection between the element and the invariant
				inv_pg = pplf.ppl_functions.intersection(elem_aux,inv_poly)
				dyn_pg = pplf.ppl_functions.get_hybridization_poly(dyn,inv_var_dict,element)
				
#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		START	#
#***********************************************************************************************************#

				# Check if the diameter of the dynamical polyhedron is greater
				# than the fixed value diameter_bound
				opt_value,xopt,yopt = hf.optimal_distance(dyn_pg)
				print('opt_value =',opt_value)
				print('xopt =',xopt)
				print('yopt =',yopt)
				
				# in case it is greater, compute a new predicate
#				if opt_value > diameter_bound:
				if opt_value >= diameter_bound:

					max_diameter = max(opt_value, max_diameter)
					
					xopt_vector = vector(xopt.values())
					xopt_normalized = xopt_vector.normalized()
					print('xopt_normalized =',xopt_normalized)

					yopt_vector = vector(yopt.values())
					yopt_normalized = yopt_vector.normalized()
					print('yopt_normalized =',yopt_normalized)

					normal_vector_dyn = yopt_normalized - xopt_normalized
					print('normal vector in dynamics =',normal_vector_dyn)

					print('dyn string =',dyn)
					dyn_array = hf.str2array(dyn,var_dict,inv_var_dict)
					print('dyn_array =',dyn_array)

#					normal_vector = hf.solve_linear_system_integer(dyn_array,normal_vector_dyn)
#					print 'integer normal vector =',normal_vector

					normal_vector_array = array(normal_vector_dyn)
					print('normal_vecto_array =',normal_vector_array)
					hyperplane_coefficients = dot(normal_vector_array,dyn_array)
					print('hyperplane_coefficients =',hyperplane_coefficients)
			
					hyperplane_coefficients_integer = hf.real2integer(hyperplane_coefficients)
					print('hyperplane_coefficients_integer =',hyperplane_coefficients_integer)

					new_LE_coeffs.append(hyperplane_coefficients_integer)

#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		END		#
#***********************************************************************************************************#
				
				PG.add_node(node_pg)
				PG.add_node(node_pg,inv=inv_pg,dyn=dyn_pg)
				
				# Store the element participating in the node creation
				mark_E.append(element)
                
				node_pg_list.append(node_pg)
				#node_elem_list.append(node+','+str(element))
				node_elem_list.append([node,element])
        
		# Add edges for the case of having loc1=loc2 in PG
		for n1 in node_pg_list:
			
			aux_list = node_pg_list[:]
			aux_list.remove(n1)
            
			for n2 in aux_list:

				guard_pg = NNC_Polyhedron(dim,'universe')
				PG.add_edge(n1,n2,guard=guard_pg)
		
		# Node relation list [[node_lg_1,[node_pg,node_pg,...]][node_lg_2,[node_pg,node_pg,...]],...]
		node_pg_rel_list.append([node,node_pg_list])
		node_rel_list.append([node,node_elem_list])
	
	f.file_creation.store_node_pg(node_pg_rel_list,node_rel_list,output)
	
	# Add edges for the nodes of PG if there is an edge in LG
	for edge in LG.edges():
        
		loc1_lg = edge[0]
		loc2_lg = edge[1]
        
		for rel in node_pg_rel_list:
			loc = rel[0]
			if loc == loc1_lg: loc1_pg_list = rel[1]
			else:
				if loc == loc2_lg: loc2_pg_list = rel[1]
    
		for loc1_pg in loc1_pg_list:
			for loc2_pg in loc2_pg_list:

				guard_pg = LG[loc1_lg][loc2_lg]['guard']
				PG.add_edge(loc1_pg,loc2_pg,guard=guard_pg)


#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		START	#
#***********************************************************************************************************#

	# Delete repeated coefficients for the new predicates
	new_unique_LE_coeffs = []
#	print 'new_LE_coeffs =',new_LE_coeffs
	for coeff_list in new_LE_coeffs:
		if coeff_list not in new_unique_LE_coeffs:
			new_unique_LE_coeffs.append(coeff_list)

	print('new_unique_LE_coeffs =',new_unique_LE_coeffs)


	# Transform the new predicates into ppl.Linear_Expression and add to the current LE
	new_LE = [] + LE
	for new_le_coeff_list in new_unique_LE_coeffs:
		new_le = Linear_Expression(new_le_coeff_list,0)
		new_LE.append(new_le)


#	# The maximum diameter for the dynamics arising with the new linear expressions will
#	# approximately the half of the current max_diameter
#	max_diameter = max_diameter/2.0

#***********************************************************************************************************#
#		NEW HYBRIDIZATION CODE																		END		#
#***********************************************************************************************************#

	# Remove repetitions from E
#	E = []
#	for e in mark_E:
#		if e not in E:
#			E.append(e)
#
#	for auxx_e in auxx_E:
#		if auxx_e not in E:
#			E.append(auxx_e)


	return PG,auxx_E,new_LE,max_diameter,creation_time


#----------------------------------------------------------------------------------------------#
def LHA_to_PHA_maximal_unif(LG,LE,var_dict,inv_var_dict,namefolder):
	
	""" A Linear Hybrid Automaton (LHA) expressed as a graph will be
		transformed into a Polyhedral Hybrid Automaton (PHA), by just
		considering the maximal elements, so the elements with affine
		dimension equal to the space dimension.
		-----------------------------------------------------------------------
		input: 	LG				linear hybrid automaton graph
				LE				homogeneous predicate coefficients matrix
				var_dict
				inv_var_dict
				namefolder		folder name for the files will be created
		output:	PG				polyhedral hybrid automaton graph
				aux_E			maximal elements
				creation_time	runtime. """
	

	# Borrar mas tarde
	global npg_line, npg_dict
	npg_line = ''
	npg_dict = {}
	
	output = namefolder + '/output'
	dim = len(var_dict)
	
	PG = nx.DiGraph()

	E, creation_time = p.create_elements.create_elements(LE)
	
	""" Just consider the maximal elements """
	aux_E = []
	for e in E:
		if e.affine_dimension() == dim:
			caux_e = NNC_Polyhedron(e)
			caux_e.topological_closure_assign()
			aux_E.append(caux_e)

	mark_E = []

	
	"""  Systems of constraints defining the elements """
	c_E = []
	for aux_e in aux_E:
		c_E.append(aux_e.constraints())

	print('Elements of aux_E(',len(aux_E),'):\n',)
	for aux_e in aux_E:
		print('    ',aux_e.constraints())
	
	ef_name = output +'/maximal_elements.dat'
	f.functions.list2file(c_E,ef_name)

	node_pg_rel_list = []
	node_rel_list = []
	number_node_lg = 0
	for node in LG:

		node_pg_list = []
		node_elem_list = []
		
		for element in aux_E:

			"""  We create an auxiliary closed element """

			elem_aux = NNC_Polyhedron(element)
			elem_aux.topological_closure_assign()
			
			
			inv_poly = LG.nodes[node]['inv']


			""" check if the element is contained in the invariant """
			if inv_poly.contains(element):
				
				dyn = LG.nodes[node]['dyn']

				node_pg = 'loc'+str(number_node_lg)
				number_node_lg = number_node_lg + 1
				
				""" check the intersection between the element and the invariant """
				inv_pg = pplf.ppl_functions.intersection(elem_aux,inv_poly)
				
				""" transform the linear dynamics to polyhedral dynamics """
				dyn_pg = pplf.ppl_functions.get_hybridization_poly(dyn,inv_var_dict,element)
				
				
				PG.add_node(node_pg)
				PG.add_node(node_pg,inv=inv_pg,dyn=dyn_pg)
				""" Store the element participating in the node creation """
				mark_E.append(element)
				
				node_pg_list.append(node_pg)
				node_elem_list.append([node,element])
	
		print('\n---------------------------------------------------------------------------------------------')
		print('Nodes in polyhedral graph with invariant',inv_poly.constraints())
		print('---------------------------------------------------------------------------------------------')
		for node_pg in node_pg_list:
			print(node_pg)
			print('     ', PG.nodes[node_pg]['inv'].constraints())
	
		""" Add edges for the case of having loc1=loc2 in PG """
		for n1 in node_pg_list:
			
			aux_list = node_pg_list[:]
			aux_list.remove(n1)
			
			for n2 in aux_list:

				n1_inv = PG.nodes[n1]['inv']
				n2_inv = PG.nodes[n2]['inv']

				if hf.smt_transition_question(n1_inv,n2_inv,dyn,inv_var_dict,var_dict,namefolder):
					guard_pg = NNC_Polyhedron(dim,'universe')
					PG.add_edge(n1,n2,guard=guard_pg)

		""" Node relation list [[node_lg_1,[node_pg,node_pg,...]][node_lg_2,[node_pg,node_pg,...]],...] """
		node_pg_rel_list.append([node,node_pg_list])
		node_rel_list.append([node,node_elem_list])
	
	print()
	print('-----------------------------------------------------------------------------------------------')

	f.file_creation.store_node_pg(node_pg_rel_list,node_rel_list,output)
	
	""" Add edges for the nodes of PG if there is an edge in LG """
	for edge in LG.edges():
		
		loc1_lg = edge[0]
		loc2_lg = edge[1]
		
		for rel in node_pg_rel_list:
			loc = rel[0]
			if loc == loc1_lg: loc1_pg_list = rel[1]
			else:
				if loc == loc2_lg: loc2_pg_list = rel[1]
	
		for loc1_pg in loc1_pg_list:
			for loc2_pg in loc2_pg_list:

				loc1_pg_inv = PG.nodes[loc1_pg]['inv']
				loc2_pg_inv = PG.nodes[loc2_pg]['inv']

				if hf.smt_transition_question(loc1_pg_inv,loc2_pg_inv,dyn,inv_var_dict,var_dict,namefolder):
					guard_pg = LG[loc1_lg][loc2_lg]['guard']
					PG.add_edge(loc1_pg,loc2_pg,guard=guard_pg)


	return PG,aux_E,creation_time


