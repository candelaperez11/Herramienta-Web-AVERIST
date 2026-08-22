import sys



#----------------------------------------------------------------------------------- 15/06/2016 ---#
def user_questions():


	""" INPUT data for the Main program """
	""" Kind of hybrid automaton (linear or polyhedral). """
	HA_type = input('What kind of hybrid automaton? (linear/polyhedral)\n')
	
	if HA_type != 'linear' and HA_type != 'polyhedral':
		sys.exit('Wrong answer')


	""" Name file path containing the input automaton text file. """
	namefile = input('\n* Please specify the name file path for the experiment data input file (experiment.dat):\n')


	""" Set the way of choosing the linear expressions for partitioning the state space, manually by providing them into a file or automatically by
		determining the partition size. """
	am_answer = input('\n* Do you want the linear expressions for creating the regions to be generated automatically (A) or do you want to add them manually (M)? Enter A/M:\n')

	if am_answer == 'A':
	
		given_linear_exp = 'nle'
		unif_linear_exp = int(input('\n* The linear expressions will be generated in a uniform fashion. Please specify the granularity -- a natural number (higher number indicates finer partition):\n'))
	
		if unif_linear_exp < 0: sys.exit('Wrong value')


	elif am_answer == 'M':

		given_linear_exp = 'le'
		unif_linear_exp = -1
		print('\nPlease specify the linear expressions for generating the regions in linearexp.dat\n')

	else:
		sys.exit('Wrong answer')

	""" Specify if the linear expressions involved in the input hybrid automaton definition are added to the set for partitioning the state space. """
	extract_answer = input('\n* In addition, do you want to add the linear expressions appearing in the input hybrid automaton? Enter Y/N:\n')

	if extract_answer == 'Y':
		extract_linear_exp = 'exle'
	elif extract_answer == 'N':
		extract_linear_exp = 'nexle'
	else:
		sys.exit('Wrong answer')


	""" Maximum CEGAR iteration: bound in the CEGAR algorithm iterations to abort the loop in case of not
		obtaining any answer about stability or instability of the hybrid automaton. """
	max_CEGAR_iteration = int(input('\n* Please specify the maximum number of CEGAR iterations:\n'))
	
	if max_CEGAR_iteration < 0:
		sys.exit('Wrong value')

	""" Specify if the linear expressions involved in cegar refinement are added by uniform creation or by separation selected predicates. """
	cegar_ref = input('\n* Do you want to add the linear expressions for refinement creating uniformly or selecting by considering the counterexample? Enter unif/selected:\n')
	
	if cegar_ref != 'unif' and cegar_ref != 'selected':
		sys.exit('Wrong answer')
	
	if cegar_ref == 'unif':
		
		unif_linear_exp_cegar = int(input('\n* The linear expressions will be generated in a uniform fashion. Please specify the granularity -- a natural number (higher number indicates finer partition):\n'))
		
		if unif_linear_exp < 0: sys.exit('Wrong value')

	elif cegar_ref == 'selected':
		unif_linear_exp_cegar = -1

	else:
		sys.exit('Wrong answer')


	""" Optimization solver choice for the mixed linear integer programming problem involved in the weight computation. """
	opt_solver = int(input('What optimization solver do you want to use for abstraction computation? Enter 1/2:\n   1: GLPK solver\n    2: PPL solver\n'))

	if opt_solver != 1 and opt_solver != 2 and opt_solver != 3:
		sys.exit('Wrong answer')
	



	return HA_type, namefile, given_linear_exp, unif_linear_exp, extract_linear_exp, max_CEGAR_iteration, cegar_ref, unif_linear_exp_cegar, opt_solver

		

	



