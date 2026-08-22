import ppl_functions as pplf
from ppl import *
from . import smt_functions as smtf
import sys


#----------------------------------------------------------------------------------------------#
def validation(WG,counterexample,output):

	""" Given the abstract weighted graph and the abstract counterexample, so a cycle on it,
	the possibility of having an execution following such cycle is analyzed.
		
		input:	WG					weighted_graph								networkx.DiGraph
				counterexample		list of WG nodes							list of networkx.DiGraph.nodes
				output				folder name to write an smt problem			string
		
		output:	refinement_type		0: no refinement							integer
									1: post-reach refinement
									2: weight refinement
				pre_comppoly		relation polyhedron before emptiness		ppl.NNC_Polyhedron
									or after one cycle if there is no 
									emptiness. """
	
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

	comppoly,pre_comppoly = pplf.relation_reach.composition(relation_list)
	print('comppoly =',comppoly.constraints())
	print('pre_comppoly =',pre_comppoly.constraints())
	print('------------------------------------------')

	if comppoly.is_empty():
		# There does not exist concrete_counterexample
		refinement_type = 1
		print('There will be post reach refinement because of comppoly emptiness or uniform refinement')
	else:
		#look for alpha
		alpha_restricted = True		# This means alpha will be restricted to be greater than one
		smtstr = smtf.smt_trans_relpoly(comppoly,alpha_restricted)
		print('SMT STRING =',smtstr)
		alpha_greater_than_one = smtf.run_smt(smtstr,output)
		#print('smtstr with alpha > 1 \n', smtstr
		print('alpha_greater_than_one =',alpha_greater_than_one,'\n')
		#		sys.exit('Esta mierda parece no funcionar')
		
		if alpha_greater_than_one:
			
			# There exists concrete_counterexample
			refinement_type = 0
			print('There will be no refinement')
		
		else:

			alpha_restricted = False	# This means alpha will be restricted to be less or equal than one (it is always greater than zero under our construction)
			smtstr = smtf.smt_trans_relpoly(comppoly,alpha_restricted)
			print('SMT STRING =',smtstr)
			alpha_less_than_one = smtf.run_smt(smtstr,output)
			#print('smtstr with alpha < 1 \n', smtstr
			print('alpha_less_than_one =',alpha_less_than_one,'\n')


			if alpha_less_than_one:
				# We do not know wether there exists concrete_counterexample or not
				refinement_type = 2
				print('There will be refinement based on weights or uniform refinement')
					
			else:
				# There does not exist concrete_counterexample
				refinement_type = 1
				print('There will be post reach refinement because of inexistence of alpha or uniform refinement')
				
	print('-------------------------------------------------- End of validation ---')


	return refinement_type,pre_comppoly


