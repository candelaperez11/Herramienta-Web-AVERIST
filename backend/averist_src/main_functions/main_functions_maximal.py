import numpy as np
import files as f
import partition as par
import sys
import hybridization as hyb
import ppl_functions as pplf
from ppl.polyhedron import NNC_Polyhedron
import networkx as nx
import refinement as ref

#----------------------------------------------------------------------------------------------#
def initial_LE(P,given_linear_exp,extract_linear_exp,unif_linear_exp,inv_var_dict,namefolder):
	
	""" Construction of the linear expression matrix for the first CEGAR iteration. """
	
	strLE = []

	if given_linear_exp == 'le':
		
		aux_ind = len(namefolder.split('/')[-1])
		newnamefolder = namefolder[0:-aux_ind]
		
		strLE = f.functions.load(newnamefolder+'linearexp.dat')

	if extract_linear_exp == 'exle':
		PLE = f.functions.transform_P(P)
		strLE = strLE + PLE
		
	if unif_linear_exp > -1:
		ULE = par.create_linear_exp.linear_expressions(unif_linear_exp,inv_var_dict)
		strLE = strLE + ULE

	if not strLE:
		sys.exit('There is no any linear expression to partition the state-space')

	strLE = list(set(strLE))

	# Now LE is transformed into a list of ppl.linear expressions
	LE = pplf.ppl_functions.get_linearexps(strLE,inv_var_dict)

	return LE



#----------------------------------------------------------------------------------------------#
def transformation_unif(G,LE,var_dict,inv_var_dict,namefolder_le):
	
	""" Automaton transformation: from linear hybrid automaton to polyhedral hybrid automaton,
		following the computational explanation in 'An algorithmic approach to stability verification
		of polyhedral switched systems', ACC 2014 . """
	
	PG,E,creation_time = hyb.automaton_transformation.LHA_to_PHA_maximal_unif(G,LE,var_dict,inv_var_dict,namefolder_le)
	
	return PG,E,creation_time



#----------------------------------------------------------------------------------------------#
def check_explosion(G):
	
	""" Checks for the case of explosion, by asking if the invariants intersect with its dynamics 
	polyhedron. """
	
	explosion = False

	for n in G.nodes():
		invpoly = NNC_Polyhedron(G.nodes[n]['inv'])
		dynpoly = G.nodes[n]['dyn']
		print('invpoly before =',invpoly.constraints())
		print('dynpoly before =',dynpoly.constraints())
		# Check if dynpoly is just the point zero. In case of being zero there is no movement
		# and therefore explosion is not possible.
		if not pplf.ppl_functions.is_zero(dynpoly):
			# Compute the closed dynamics polyhedron (to avoid a not bounded problem in optimization)
			cdynpoly = pplf.ppl_functions.copy_closed_polyhedron(dynpoly)
			invpoly.intersection_assign(cdynpoly)
			if not invpoly.is_empty() and not pplf.ppl_functions.is_zero(invpoly):
				print('invpoly =',invpoly.constraints())
				print('dynpoly =',dynpoly.constraints())
				explosion = True
				break

	return explosion



#----------------------------------------------------------------------------------------------#
def refinement(WG,counterexample,refinement_type):
	
	if refinement_type == 1:
		separation_linearexp_list = ref.refinement.refinement_type_1(WG,counterexample)
	else:								# In this case refinement type is 2
		#separation_linearexp_list = ref.refinement.refinement_type_2(WG,counterexample)
		separation_linearexp_list = ref.refinement.refinement_type_3(WG,counterexample)
#		if separation_linearexp_list == []:
#			How to choose the separation linear expression? (maybe in an uniform fashion)
	
	return separation_linearexp_list



