import ppl_functions as pplf
from . import refinement_functions as rf
from ppl import *

import sys


#----------------------------------------------------------------------------------------------#
def refinement_type_1(WG,counterexample):

	""" Given the abstract weighted graph and the abstract counterexample, so a cycle on it,
	the possibility of having an execution following such cycle is analyzed.
		
		input:	WG					weighted_graph							networkx.DiGraph
				counterexample		list of WG nodes						list of networkx.DiGraph.nodes
				output				folder name to write an smt problem		string
		
		output:	linearexplist		new linear expressions for refinement	list of ppl.Linear_Expression """

	relation_list = []
	lencex = len(counterexample)
	for i in range(lencex-1):
		precnode = counterexample[i]
		poscnode = counterexample[i+1]
		relation_list.append(WG.edges[precnode, poscnode]['relation'])

	print('Relation list = \n',)
	for r in relation_list:
			print(r.constraints())
	print('------------------------------------------')


	empty = False
	iteration = 0
	reldim = relation_list[0].space_dimension()
	initrelpoly = NNC_Polyhedron(reldim,'universe')

	while not empty:

		nodeind,comppoly,pre_comppoly = pplf.relation_reach.composition_ref(initrelpoly,relation_list)
		print('node index =',nodeind)
		print('comppoly =',comppoly.constraints())
		print('pre_comppoly =',pre_comppoly.constraints())
		print('------------------------------------------')

		if comppoly.is_empty():
			empty = True
		else:
			initrelpoly = NNC_Polyhedron(comppoly)
			
# ------------------------------------------------------------------------ 18/01/2017 --- BEGIN
		# In case of not getting emptiness of the composed polyhedron after 100 iterations
		# then weighted reachability is performed by recomputing the relation_list
		if iteration == 100:
			
			weight_list = []
			for i in range(lencex-1):
				precnode = counterexample[i]
				poscnode = counterexample[i+1]
				weight_list.append(WG.edges[precnode, poscnode]['weight'])

			# Transform relation_list into weighted_relation_list

			epsilon = rf.obtain_epsilon(weight_list)
			interval_weighted_relation_list = []
			for i in range(len(relation_list)):
				interval_weighted_relation_list.append(pplf.weighted_relation_reach.interval_weight_poly_rel_restriction(relation_list[i],weight_list[i],epsilon))

			initrelpoly = NNC_Polyhedron(reldim,'universe')
	
		# In case of not getting emptiness of the composed polyhedron after 200 iterations
		# averist will finish
		if iteration == 200:
			sys.exit ('Not found separating hyperplane')

# ------------------------------------------------------------------------ 18/01/2017 --- END

		iteration += 1
		
		print('iteration cycle =', iteration)
	
	# The post reach set is the projection of pre_comppoly in the last half of the variables
	postcoordlist = range(reldim//2,reldim)
	relpostpoly = pplf.ppl_functions.projection(pre_comppoly,postcoordlist)
	postpoly = pplf.ppl_functions.reduce_var(relpostpoly,postcoordlist)
	
	# Compute pre reach set between nodes with index nodeind and nodeind+1
	#pre_relpoly = relation_list[nodeind]
	pre_relpoly = relation_list[nodeind]
	precoordlist = range(reldim//2)
	relprepoly = pplf.ppl_functions.projection(pre_relpoly,precoordlist)
	prepoly = pplf.ppl_functions.reduce_var(relprepoly,precoordlist)
			
	# Get the element the nodes for refinement go through
#	prenode = counterexample[nodeind]
#	posnode = counterexample[nodeind + 1]
#	element_through = WG.edges[prenode, posnode]['element']
			
	# Get a list of one or more separating hyperplanes
	#sep_linexp_list = rf.separating_hyperplane_list(postpoly,prepoly)
	sep_linexp = rf.separating_hyperplane(postpoly,prepoly)
			
	if sep_linexp == None:
		sys.exit('There is no separating hyperplane')
	else:
		return sep_linexp



#----------------------------------------------------------------------------------------------#
def refinement_type_2(WG,counterexample):
	
	""" Given the abstract weighted graph and the abstract counterexample, so a cycle on it,
		the possibility of having an execution following such cycle is analyzed.
		
		input:	WG					weighted_graph							networkx.DiGraph
		counterexample		list of WG nodes						list of networkx.DiGraph.nodes
		output				folder name to write an smt problem		string
		
		output:	linearexplist		new linear expressions for refinement	list of ppl.Linear_Expression """
	
	relation_list = []
	weight_list = []
	lencex = len(counterexample)
	for i in range(lencex-1):
		precnode = counterexample[i]
		poscnode = counterexample[i+1]
		relation_list.append(WG.edges[precnode, poscnode]['relation'])
		weight_list.append(WG.edges[precnode, poscnode]['weight'])

	print('Relation list = \n',)
	for r in relation_list:
		print(r.constraints())
	print('------------------------------------------')


	empty = False
	iteration = 0
	reldim = relation_list[0].space_dimension()
	initrelpoly = NNC_Polyhedron(reldim,'universe')
	
	while not empty:
		
		nodeind,comppoly,pre_comppoly = pplf.weighted_relation_reach.weighted_composition_ref(initrelpoly,relation_list,weight_list)
		print('node index =',nodeind)
		print('comppoly =',comppoly.constraints())
		print('pre_comppoly =',pre_comppoly.constraints())
		print('------------------------------------------')
		
		#sys.exit()
		
		if comppoly.is_empty():
			empty = True
		else:
			initrelpoly = NNC_Polyhedron(comppoly)
		
		iteration += 1
		
		print('iteration cycle =', iteration)


	# The post reach set is the projection of pre_comppoly in the last half of the variables
	postcoordlist = range(reldim/2,reldim)
	relpostpoly = pplf.ppl_functions.projection(pre_comppoly,postcoordlist)
	postpoly = pplf.ppl_functions.reduce_var(relpostpoly,postcoordlist)
	
	print('pre_comppoly =',pre_comppoly.constraints())
	print('projection last half variables =',relpostpoly.constraints())
	print('reduced variables =',postpoly.constraints(),'\n')

	# Compute pre reach set between nodes with index nodeind and nodeind+1
	#pre_relpoly = relation_list[nodeind]
	pre_relpoly = relation_list[nodeind]
	precoordlist = range(reldim//2)
	relprepoly = pplf.ppl_functions.projection(pre_relpoly,precoordlist)
	prepoly = pplf.ppl_functions.reduce_var(relprepoly,precoordlist)
	
	print('pre_relpoly =',pre_relpoly.constraints())
	print('projection =',relprepoly.constraints())
	print('reduced variables =',prepoly.constraints(),'\n')

	# Get the element the nodes for refinement go through
	#	prenode = counterexample[nodeind]
	#	posnode = counterexample[nodeind + 1]
	#	element_through = WG.edges[prenode, posnode]['element']

	# Get a list of one or more separating hyperplanes
	#sep_linexp_list = rf.separating_hyperplane_list(postpoly,prepoly)
	sep_linexp = rf.separating_hyperplane(postpoly,prepoly)
	#print('sep_linexp =',sep_linexp
	if sep_linexp == None:
		sys.exit('There is no separating hyperplane')
	else:
		return sep_linexp


#----------------------------------------------------------------------------------------------#
def refinement_type_3(WG,counterexample):
	
	""" Given the abstract weighted graph and the abstract counterexample, so a cycle on it,
		the possibility of having an execution following such cycle is analyzed.
		
		input:	WG					weighted_graph							networkx.DiGraph
				counterexample		list of WG nodes						list of networkx.DiGraph.nodes
				output				folder name to write an smt problem		string
		
		output:	linearexplist		new linear expressions for refinement	list of ppl.Linear_Expression """
	
	relation_list = []
	weight_list = []
	lencex = len(counterexample)
	for i in range(lencex-1):
		precnode = counterexample[i]
		poscnode = counterexample[i+1]
		relation_list.append(WG.edges[precnode, poscnode]['relation'])
		weight_list.append(WG.edges[precnode, poscnode]['weight'])
	
	print('Relation list = \n',)
	for r in relation_list:
		print(r.constraints())
	print('------------------------------------------')


#	Transform relation_list into weighted_relation_list

	epsilon = rf.obtain_epsilon(weight_list)
	interval_weighted_relation_list = []
	for i in range(len(relation_list)):
		interval_weighted_relation_list.append(pplf.weighted_relation_reach.interval_weight_poly_rel_restriction(relation_list[i],weight_list[i],epsilon))

	print('Interval weighted relation list = \n',)
	for iwr in interval_weighted_relation_list:
		print(iwr.constraints())
	print('------------------------------------------')
	
	
	empty = False
	iteration = 0
	reldim = relation_list[0].space_dimension()
	initrelpoly = NNC_Polyhedron(reldim,'universe')
	
	while not empty:
		
		nodeind,comppoly,pre_comppoly = pplf.relation_reach.composition_ref(initrelpoly,interval_weighted_relation_list)
		
		print('node index =',nodeind)
		print('comppoly =',comppoly.constraints())
		print('pre_comppoly =',pre_comppoly.constraints())
		print('------------------------------------------')
		
		#sys.exit()
		
		if comppoly.is_empty():
			empty = True
		else:
			initrelpoly = NNC_Polyhedron(comppoly)
		
		iteration += 1
		
		print('iteration cycle =', iteration)


	# The post reach set is the projection of pre_comppoly in the last half of the variables
	postcoordlist = range(reldim//2,reldim)
	relpostpoly = pplf.ppl_functions.projection(pre_comppoly,postcoordlist)
	postpoly = pplf.ppl_functions.reduce_var(relpostpoly,postcoordlist)
	
	print('pre_comppoly =',pre_comppoly.constraints())
	print('projection last half variables =',relpostpoly.constraints())
	print('reduced variables =',postpoly.constraints(),'\n')
	
	# Compute pre reach set between nodes with index nodeind and nodeind+1
	#pre_relpoly = relation_list[nodeind]
	pre_relpoly = interval_weighted_relation_list[nodeind]
	precoordlist = range(reldim//2)
	relprepoly = pplf.ppl_functions.projection(pre_relpoly,precoordlist)
	prepoly = pplf.ppl_functions.reduce_var(relprepoly,precoordlist)
	
	print('pre_relpoly =',pre_relpoly.constraints())
	print('projection =',relprepoly.constraints())
	print('reduced variables =',prepoly.constraints(),'\n')
	
	# Get the element the nodes for refinement go through
	#	prenode = counterexample[nodeind]
	#	posnode = counterexample[nodeind + 1]
	#	element_through = WG.edges[prenode, posnode]['element']
	
	# Get a list of one or more separating hyperplanes
	#sep_linexp_list = rf.separating_hyperplane_list(postpoly,prepoly)
	sep_linexp = rf.separating_hyperplane(postpoly,prepoly)
	#print('sep_linexp =',sep_linexp
	if sep_linexp == None:
		sys.exit('There is no separating hyperplane')
	else:
		return sep_linexp



    
