from ppl import *
import ppl_functions as pplf
from fractions import Fraction


#----------------------------------------------------------------------------------------------#
def check_separation(pospoly,prepoly,coefflist,term):
	
	""" Check if the linear expression created by a given coefficient list and an inhomogeneous
		term separates or not the post and pre polyhedra. """
	
	# Creation of linear expression
	le = pplf.ppl_functions.create_linearexp(coefflist,term)

	
	# CHECK IF THIS IS REALLY OK (JUST THE NEXT LINE)
	# It is working for the exp_pyramids_1, but maybe not for all
	if pospoly.is_universe() or prepoly.is_universe(): return True,le
	##################################################################
	
	# Creation of the constraints greater and less than
	constg_closed = le >= 0
	constl_open = le < 0
	
	# Creation of polyhedra with such constraints
	Pcg_closed = NNC_Polyhedron(constg_closed)
	Pcl_open = NNC_Polyhedron(constl_open)

	# Check conditions for separability
	Pcg_closed_pos = NNC_Polyhedron(Pcg_closed)
	Pcg_closed_pos.intersection_assign(pospoly)
	Pcg_closed_pre = NNC_Polyhedron(Pcg_closed)
	Pcg_closed_pre.intersection_assign(prepoly)
	Pcl_open_pos = NNC_Polyhedron(Pcl_open)
	Pcl_open_pos.intersection_assign(pospoly)
	Pcl_open_pre = NNC_Polyhedron(Pcl_open)
	Pcl_open_pre.intersection_assign(prepoly)
	
	cond1 = Pcg_closed_pos.is_empty()
	cond2 = Pcl_open_pre.is_empty()
	cond3 = Pcl_open_pos.is_empty()
	cond4 = Pcg_closed_pre.is_empty()
	
	
	# Creation of the constraints greater and less than
	constg_open = le > 0
	constl_closed = le <= 0
	
	# Creation of polyhedra with such constraints
	Pcg_open = NNC_Polyhedron(constg_open)
	Pcl_closed = NNC_Polyhedron(constl_closed)
	
	# Check conditions for separability
	Pcg_open_pos = NNC_Polyhedron(Pcg_open)
	Pcg_open_pos.intersection_assign(pospoly)
	Pcg_open_pre = NNC_Polyhedron(Pcg_open)
	Pcg_open_pre.intersection_assign(prepoly)
	Pcl_closed_pos = NNC_Polyhedron(Pcl_closed)
	Pcl_closed_pos.intersection_assign(pospoly)
	Pcl_closed_pre = NNC_Polyhedron(Pcl_closed)
	Pcl_closed_pre.intersection_assign(prepoly)
	
	
	cond5 = Pcg_open_pos.is_empty()
	cond6 = Pcl_closed_pre.is_empty()
	cond7 = Pcl_closed_pos.is_empty()
	cond8 = Pcg_open_pre.is_empty()
	
	
	if (cond1 and cond2) or (cond3 and cond4) or (cond5 and cond6) or (cond7 and cond8):
		#print( 'sepbool is true')
		sepbool = True
	else:
		#print( 'sepbool is false')
		sepbool = False
	
	return sepbool,le



#----------------------------------------------------------------------------------------------#
def separating_hyperplane(pospoly,prepoly):

	""" Obtain a separating linear expression list which separates post polyhedron and 
		pre polyhedron. """

	posconstlist = pospoly.minimized_constraints()
	preconstlist = prepoly.minimized_constraints()
	
	print( 'dim pospoly =',pospoly.space_dimension())
	print( 'dim prepoly =',prepoly.space_dimension())
	
	print( 'pospoly =',pospoly.constraints())
	print( 'prepoly =',prepoly.constraints())
	
	print( 'posconstlist =',posconstlist)
	print( 'preconstlist =',preconstlist)


	for posc in posconstlist:
		
		coefflist = posc.coefficients()
		term = posc.inhomogeneous_term()
		sepbool,hyperplane_le = check_separation(pospoly,prepoly,coefflist,term)

		if sepbool == True:
			return [hyperplane_le]

	for prec in preconstlist:
		coefflist = prec.coefficients()
		term = prec.inhomogeneous_term()
		sepbool,hyperplane_le = check_separation(pospoly,prepoly,coefflist,term)

		if sepbool == True:
			return [hyperplane_le]

	return None
#	return [Linear_Expression(3*Variable(1)-Variable(2))]




#----------------------------------------------------------------------------------------------#
def check_total_weight(weightlist,epsilon):
	
	""" Check that the product of w-eps is greater than one. """

	totalweight = 1
	
	for weight in weightlist:

		totalweight = totalweight * (weight - epsilon)

	if (totalweight > 1.):
		return True
	else:
		return False



#----------------------------------------------------------------------------------------------#
def obtain_epsilon(weightlist):
	
	""" Obtain the epsilon to determine weight intervals [w-eps,w+eps] which keep the
		total weight greater than one. """

	# Fix an initial epsilon
	epsilon = 1
	greaterthanone = False
	
	while not greaterthanone:
		epsilon = Fraction(epsilon,10)
		greaterthanone = check_total_weight(weightlist,epsilon)

	return epsilon
















