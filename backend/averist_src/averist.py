import main_functions as mf
import time
import files as f
import input_parser as ip
import partition as p
import os

""" It asks for the INPUT data. """
HA_type, namefile, given_linear_exp, unif_linear_exp, extract_linear_exp, max_CEGAR_iteration, cegar_ref, unif_linear_exp_cegar, opt_solver = mf.questions.user_questions()


""" Set the initial time value. """
absolute_time = time.time()


""" Creates the necessary folder to store general information about the results. """
namefolder = os.path.splitext(namefile)[0]+'_averist'
f.file_creation.folders(namefolder)

print('-----------------------------------------------------------------------------------')
print('namefile =', namefile)
print('namefolder =', namefolder)
print('HA_type = ', HA_type)
print('-----------------------------------------------------------------------------------')

""" Reads the input automaton. """
var_dict,inv_var_dict,P,G = ip.read_input.read_input(namefile,HA_type)

print('var_dict =', var_dict)
print('inv_var_dict =', inv_var_dict)
print('P =', P)
print('Nodes of G =',G.nodes())
print('Edges of G =',G.edges())
print('-----------------------------------------------------------------------------------')


""" Stores the input automaton graph into a file. """
f.file_creation.store_graph(G,namefolder,HA_type)


""" Construction of the linear expression matrix. """
LE = mf.main_functions_maximal.initial_LE(P,given_linear_exp,extract_linear_exp,unif_linear_exp,inv_var_dict,namefolder)
print('LE =',LE)
print('-----------------------------------------------------------------------------------')

""" Creates the necessary folders to store information about the results. """
namefolder_le = f.file_creation.itfolders(LE,namefolder)

""" Stores the linear expressions into a file. """
f.file_creation.store_le(LE,namefolder_le+'/output')

if HA_type == 'polyhedral':
	
	""" Call cegar loop for a polyhedral switched system. """
	answer, element_creation_total_time,automaton_transf_total_time,abstraction_total_time,subgraph_total_time,optimization_total_time,verification_total_time,validation_total_time,refinement_total_time = mf.cegar_loop_functions.polyhedral_cegar_loop(G,LE,var_dict,inv_var_dict,namefolder,max_CEGAR_iteration,cegar_ref,unif_linear_exp_cegar,opt_solver)
	

else:	# HA_type = 'linear'
	
	""" Call cegar loop for a polyhedral switched system. """
	answer, element_creation_total_time,automaton_transf_total_time,abstraction_total_time,subgraph_total_time,optimization_total_time,verification_total_time,validation_total_time,refinement_total_time = mf.cegar_loop_functions.linear_cegar_loop(G,LE,var_dict,inv_var_dict,namefolder,max_CEGAR_iteration,cegar_ref,unif_linear_exp_cegar,opt_solver)
	

if answer == False: print('WE DID NOT GET ANY ANSWER')

absolute_time = time.time() - absolute_time
at = open(namefolder+'/output/absolute_time.dat','w')
at.write('Absolute time =' + str(absolute_time) + 'seconds\n')
at.close()

f.file_creation.store_total_time(element_creation_total_time,automaton_transf_total_time,abstraction_total_time,subgraph_total_time,optimization_total_time,verification_total_time,validation_total_time, refinement_total_time,absolute_time,namefolder)









	
		

	



