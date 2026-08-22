import time
import files as f
from . import main_functions_maximal as mfm
import partition as p
import abstraction as a
import prune as prn
import model_check as mc
import validation as v




#----------------------------------------------------------------------------------------------#
def abstraction_verification_validation_refinement(E,PG,namefolder_le,HA_type,opt_solver,cegar_ref):
	
	""" Constructs the abstract graph. """
	abstraction_time = time.time()
	print('E=',)
	for e in E:
		print(e.constraints())
	WG,subgraph_time,optimization_time = a.weighted_graph.construct_weighted_graph(PG,E,opt_solver)
	abstraction_time = time.time() - abstraction_time
		
		
		
	print('WG nodes(data=True)')
	for wgn in WG.nodes(data=True):
		print(wgn)
	print('WG edges ')
	for wge in WG.edges():
		print(wge)
		print('weight=',WG.edges[wge[0], wge[1]]['weight'])
		print('element =',WG.edges[wge[0], wge[1]]['element'].constraints())
		print('relation =',WG.edges[wge[0], wge[1]]['relation'].constraints())
		print('\n')

	
	""" Stores the abstract graph. """
	f.file_creation.store_WG(WG,namefolder_le+'/output/weighted_graph.dat')
	#sys.exit('Abstract weighted graph constructed and stored.')
		
	""" Pruning of the weighted graph to delete not necessary self loops. """
	prn_WG = prn.graph_pruning.delete_selfloops(WG)
		
	""" Pruning to delete some not necessary nodes and edges. """
	prn_WG = prn.graph_pruning.delete_duplicate_edges(WG)
		
	""" Stores the pruned abstract graph. """
	f.file_creation.store_WG(WG,namefolder_le+'/output/pruned_weighted_graph.dat')
		
	""" Verification of the weighted abstract graph. It returns a verification message of stability
		in the input hybrid automaton or abstract counterexample found. In case there is an abstract
		counterexample, this is also returned. The abstract counterexample is a cycle in the weighted
		abstract graph with total weight greater than one. """
	verification_time = time.time()
	verification_msg,counterexample = mc.verification.verification(prn_WG)
	verification_time = time.time() - verification_time
		
	print('verification_msg =', verification_msg)
	#sys.exit('Verification performed.')
	""" In case of abstract counterexample existence, a validation is performed in order to search
		either for a violation of stability in the input hybrid automaton, a concrete counterexample,
		or for information on how to proceed for a refinement. """
	# Define the list of separating linear expressions as an empty list, for the case of not computing it.
	separation_linearexp_list = []
	# Initialize answer as False
	answer = False
	
	if (verification_msg == 'Stable'):
		
		answer = True
		stability_msg = verification_msg
		validation_time = 0.
		refinement_time = 0.
	
	elif (verification_msg == 'Abstract counterexample'):
		
		if HA_type == 'polyhedral':			# In the case of HA_type == 'linear' an empty separation_linearexp_list is returned
		
			print('We perform validation')
			print('counterexample =', counterexample)
				
			""" Creates the necessary folders to store information about every CEGAR iteration results. """
			f.file_creation.smtfolder(namefolder_le + '/output')
					
			validation_time = time.time()
			refinement_type,pre_comppoly = v.validation.validation(WG,counterexample,namefolder_le+'/output')
			validation_time = time.time() - validation_time
		
		
			print('refinement_type =',refinement_type)
			""" The refinement type is checked in order to get new linear expressions for refinement or stop because
				of the existence of a concrete counterexample. """
			if refinement_type == 0:
				
				answer = True
				stability_msg = 'Unstable (concrete counterexample)'
				refinement_time = 0.
				print('Unstable (concrete counterexample)')

			elif refinement_type == 1:
				
				if cegar_ref == 'unif':
				
					stability_msg = verification_msg + ' (uniform refinement)'
					print(' (uniform refinement)')
					refinement_time = 0.
				
				else:		# in this case cegar_ref = 'selected'
					
					stability_msg = verification_msg + ' (post-reach refinement)'
					print(' (post-reach refinement)')
					refinement_time = time.time()
					separation_linearexp_list = mfm.refinement(WG,counterexample,refinement_type)
					refinement_time = time.time() - refinement_time
					""" Stores the separation linear expressions if not empty. """
					if separation_linearexp_list:
						f.file_creation.store_sep_le(separation_linearexp_list,namefolder_le+'/output')

			else:							# In this case refinement_type is equal to 2
				
				if cegar_ref == 'unif':
					
					stability_msg = verification_msg + ' (uniform refinement)'
					print(' (uniform refinement)')
					refinement_time = 0.
				
				else:		# in this case cegar_ref = 'selected'

					stability_msg = verification_msg  + ' (post-reach weighted refinement)'
					print(' (post-reach weighted refinement)')
					refinement_time = time.time()
					separation_linearexp_list = mfm.refinement(WG,counterexample,refinement_type)
					refinement_time = time.time() - refinement_time
					""" Stores the separation linear expressions if not empty. """
					if separation_linearexp_list:
						f.file_creation.store_sep_le(separation_linearexp_list,namefolder_le+'/output')

		else:		# HA_type == 'linear'
			stability_msg = 'Unstable (hybridization)'
			validation_time = 0.
			refinement_time = 0.

	elif (verification_msg == 'There is no possible executions'):
		answer = True
		stability_msg = verification_msg + ' (weight refinement)'
		validation_time = 0.
		refinement_time = 0.
	
	""" Stores the stability answer. """
	print('stability_msg =', stability_msg)
	f.file_creation.store_stable_answer(stability_msg,counterexample,namefolder_le+'/output')
		

	return answer, separation_linearexp_list, abstraction_time, subgraph_time, optimization_time, verification_time, validation_time, refinement_time

	


#----------------------------------------------------------------------------------------------#
def polyhedral_cegar_loop(PG,LE,var_dict,inv_var_dict,namefolder,max_CEGAR_iteration,cegar_ref,unif_linear_exp_cegar,opt_solver):
	
	""" Set the initial time values. """
	element_creation_total_time, automaton_transf_total_time, abstraction_total_time, subgraph_total_time, optimization_total_time, verification_total_time,validation_total_time, refinement_total_time = f.functions.initialize_time()
	
	""" Checking if there is explosion in some element. In this case a further analysis
		is not needed, instability of the input hybrid system is obtained. """
	explosion = mfm.check_explosion(PG)
	print
	print('explosion =',explosion)


	answer = False
	automaton_transf_time = 0.
	
	
	""" In case of blow-up of polyhedral hybrid systems, instability is verified. """
	if explosion:
		
		""" Set the times. """
		element_creation_time = 0.
		abstraction_time = 0.
		subgraph_time = 0.
		optimization_time = 0.
		verification_time = 0.
		validation_time = 0.
		refinement_time = 0.
		total_time = 0.
		f.file_creation.store_time(element_creation_time,automaton_transf_time,abstraction_time,subgraph_time,optimization_time,verification_time,validation_time, refinement_time,total_time,namefolder)
		
		""" Stability answer (blow-up). """
		stability_msg = 'Unstable (blow-up)'
		answer = True

		""" answer is already True here, so the while loop below (which is where
			store_stable_answer is normally called) never runs. Without this call
			stable.dat is never written for the blow-up case. """
		f.file_creation.store_stable_answer(stability_msg,[],namefolder+'/output')


	iteration = 0
	
	while not answer and (iteration < max_CEGAR_iteration):
		print('iteration ',iteration)
	
		total_time = time.time()

		if iteration == 0:
			
			""" Element creation for partition. """
			E, element_creation_time = p.create_elements.create_elements(LE)
			print('E =')
			for e in E:
				print(e.constraints())
			print('element_creation_time =', element_creation_time)
			print('-----------------------------------------------------------------------------------')
					
		else:
		
			if cegar_ref == 'unif':
				unif_iteration = unif_linear_exp_cegar + iteration
				print('unif_iteration=',unif_iteration)
				print('LE before',LE)
				LE = p.create_linear_exp.add_unif_linear_expressions(unif_iteration,inv_var_dict,LE)
				print('LE after =',LE)
				E, element_creation_time = p.create_elements.create_elements(LE)
		
			else:				# In this case cegar_ref == 'selected'
				REG,FC = p.create_elements.get_regions_and_faces(E)
				new_FC,element_creation_time = p.create_elements.create_new_elements(FC,separation_linearexp_list)
				E = REG + new_FC
				for sle in separation_linearexp_list:
					LE.append(sle)
				print('new LE after',iteration,' =',LE)


		""" Creates the necessary folders to store information about the results. """
		namefolder_le = f.file_creation.itfolders(LE,namefolder)

		""" Stores the linear expressions into a file. """
		f.file_creation.store_le(LE,namefolder_le+'/output')

		""" Stores the elements into a file. """
		f.file_creation.store_elements(E,namefolder_le+'/output')


		""" Performs the abstraction construction and stability verification. Then, if a counterexample is returned,
			counterexample validation is performed. And in case of concrete counterexample, it constructs a set of
			refinement predicates. """
		answer, separation_linearexp_list, abstraction_time, subgraph_time, optimization_time, verification_time, validation_time, refinement_time = abstraction_verification_validation_refinement(E,PG,namefolder_le,'polyhedral',opt_solver,cegar_ref)

		""" Stores the times. """
		total_time = time.time() - total_time
		f.file_creation.store_time(element_creation_time,automaton_transf_time,abstraction_time,subgraph_time,optimization_time,verification_time,validation_time, refinement_time,total_time,namefolder_le)
		
		""" Sum of the times. """
		element_creation_total_time += element_creation_time
#		automaton_transf_total_time += automaton_transf_time
		abstraction_total_time += abstraction_time
		subgraph_total_time += subgraph_time
		optimization_total_time += optimization_time
		verification_total_time += verification_time
		validation_total_time += validation_time
		refinement_total_time += refinement_time

		""" Iteration increment. """
		iteration += 1

	automaton_transf_total_time = 0.
	
	return answer,element_creation_total_time,automaton_transf_total_time,abstraction_total_time,subgraph_total_time,optimization_total_time,verification_total_time,validation_total_time,refinement_total_time



#----------------------------------------------------------------------------------------------#
def linear_cegar_loop(G,LE,var_dict,inv_var_dict,namefolder,max_CEGAR_iteration,cegar_ref,unif_linear_exp_cegar,opt_solver):
	
	""" Set the initial time values. """
	element_creation_total_time, automaton_transf_total_time, abstraction_total_time, subgraph_total_time, optimization_total_time, verification_total_time,validation_total_time, refinement_total_time = f.functions.initialize_time()
	
	answer = False
	iteration = 0
	

	while not answer and (iteration < max_CEGAR_iteration):
		print('iteration',iteration)
		
		total_time = time.time()
		
		if iteration == 0:
			
			""" Element creation for partition. """
			E, element_creation_time = p.create_elements.create_elements(LE)
			print('E =')
			for e in E:
				print(e.constraints())
				print('element_creation_time =', element_creation_time)
				print('-----------------------------------------------------------------------------------')
	
		else:
			
			if cegar_ref == 'unif' or explosion_ref == 'unif':
				unif_iteration = unif_linear_exp_cegar + iteration
				print('unif_iteration=',unif_iteration)
				print('LE before',LE)
				LE = p.create_linear_exp.add_unif_linear_expressions(unif_iteration,inv_var_dict,LE)
				print('LE after =',LE)
				E, element_creation_time = p.create_elements.create_elements(LE)
			
			else:				# In this case cegar_ref == 'selected' and explosion_ref == 'void'
				REG,FC = p.create_elements.get_regions_and_faces(E)
				new_FC,element_creation_time = p.create_elements.create_new_elements(FC,separation_linearexp_list)
				E = REG + new_FC
				for sle in separation_linearexp_list:
					LE.append(sle)
				print('new LE after',iteration,' =',LE)


		""" Creates the necessary folders to store information about the results. """
		namefolder_le = f.file_creation.itfolders(LE,namefolder)
		
		""" Stores the linear expressions into a file. """
		f.file_creation.store_le(LE,namefolder_le+'/output')
		
		""" Stores the elements into a file. """
		f.file_creation.store_elements(E,namefolder_le+'/output')
		
		""" Automaton transformation in case of the input hybrid automaton is linear. """
		# In the future, we can consider different automaton transformations (norm, unif)
		automaton_transf_time = time.time()
#		PG,E,element_creation_time = mfm.transformation_unif(G,LE,var_dict,inv_var_dict,namefolder_le)
		PG,maximal_E,element_creation_time = mfm.transformation_unif(G,LE,var_dict,inv_var_dict,namefolder_le)
		automaton_transf_time = time.time() - automaton_transf_time
		
		""" Stores the transformed automaton into a file. """
		f.file_creation.store_pgraph(PG,namefolder_le)


		""" Checking if there is explosion in some element. In this case a further analysis
			is not needed, instability of the input hybrid system is obtained. """
		explosion = mfm.check_explosion(PG)
		print()
		print('explosion =',explosion)

		if explosion:
			
			""" Refinement because of explosion. """
			explosion_ref = 'unif'

			""" Set the times. """
			element_creation_time = 0.
			abstraction_time = 0.
			subgraph_time = 0.
			optimization_time = 0.
			verification_time = 0.
			validation_time = 0.
			refinement_time = 0.
			total_time = 0.
		
			""" Stability answer (blow-up). """
			stability_msg = 'Unstable (blow-up)'


		else:
			
			""" Performs the abstraction construction and stability verification. Then, if a counterexample is returned,
			counterexample validation is performed. And in case of concrete counterexample, it constructs a set of
			refinement predicates. """
			answer, separation_linearexp_list, abstraction_time, subgraph_time, optimization_time, verification_time, validation_time, refinement_time = abstraction_verification_validation_refinement(E,PG,namefolder_le,'linear',opt_solver,cegar_ref)
		
			""" Refinement because of explosion. """
			if separation_linearexp_list:
				explosion_ref = 'void'
			else:
				explosion_ref = 'unif'
		
		""" Stores the times. """
		total_time = time.time() - total_time
		f.file_creation.store_time(element_creation_time,automaton_transf_time,abstraction_time,subgraph_time,optimization_time,verification_time,validation_time, refinement_time,total_time,namefolder_le)
		
		""" Sum of the times. """
		element_creation_total_time += element_creation_time
		automaton_transf_total_time += automaton_transf_time
		abstraction_total_time += abstraction_time
		subgraph_total_time += subgraph_time
		optimization_total_time += optimization_time
		verification_total_time += verification_time
		validation_total_time += validation_time
		refinement_total_time += refinement_time
		
		""" Iteration increment. """
		iteration += 1


	return answer,element_creation_total_time,automaton_transf_total_time,abstraction_total_time,subgraph_total_time,optimization_total_time,verification_total_time,validation_total_time,refinement_total_time

	






