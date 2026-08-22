import ppl_functions as pplf
import sys
import time
# from ppl import *
from ppl import Variable, MIP_Problem
from ppl.polyhedron import NNC_Polyhedron
from sage.all import *
from fractions import Fraction



#----------------------------------------------------------------------------------- 03/11/2016 ---#
def optimization_MIP(relunitpoly,r,i):
	
	""" Obtains the solution to the optimization problem by means of the PPL solver.
		It returns the scaling value by considering the relational polyhedron relunitpoly
		and restricting the problem to the values r and i.
		input:	relunitpoly						NNC_Polyhedron
				r								integer (1 or -1)
				i								integer (variable coordinate)
		output:	sol								fractions.Fraction. """
	
	dim = relunitpoly.space_dimension()
	halfdim = dim//2

	# Define the Mixed Integer Linear Program
	m = MIP_Problem(dim)
	# Define and set the objective function
#	print('*************************************************************')
#	print('i=',i)
	objective_function_str = 'objective_function='
	for j in range(dim):
		if j == i:
			objective_function_str += '+' + str(r) + '*Variable(' + str(j) + ')'
		else:
			objective_function_str += '+0*Variable(' + str(j) + ')'

	# print('objective function string =', objective_function_str)
	# exec(objective_function_str)
	# Código corregido para Python 3 / Sage 10
	loc = {} 
	exec(objective_function_str, globals(), loc)
	objective_function = loc['objective_function']
	# print('objective function =', objective_function)
	m.set_objective_function(objective_function)
	# print('objective function in the model =', m.objective_function())

	# Construction of the closure of relunitpoly because strict inequalities cannot be added
	# to the mixed linear integer problem m
	relunitpoly_closure = NNC_Polyhedron(relunitpoly)
	relunitpoly_closure.topological_closure_assign()
	for c in relunitpoly_closure.constraints():
		#print('constraint =',c)
		m.add_constraint(c)

	if m.is_satisfiable():
		try:
			sol = m.optimal_value()
		except ValueError:
			print(ValueError)
			sol = float('inf')

#	print('sol =',sol)
	# We transform the solution sol from sage.rings.rational.Rational to fractions.Fraction
	# for later operations involved with the weight refinement.
	solf = Fraction(int(sol.numerator)/int(sol.denominator))
	return solf




#----------------------------------------------------------------------------------------------#
def optimization(relunitpoly,r,i):

	dim = relunitpoly.space_dimension()
	halfdim = dim//2
	
	p=MixedIntegerLinearProgram(maximization=True,solver="GLPK")
	x=p.new_variable(real=True)
	
	I = range(dim)
	# Objective function coefficient list
	oc = [0]*dim
	oc[i] = r
	# Set objective function
	p.set_objective(sum(oc[v]*x[v] for v in I))
	
	for c in relunitpoly.constraints():
		
		coefficient_list = c.coefficients()
		inhomogeneous_term = c.inhomogeneous_term()
		
		if c.is_equality():
			p.add_constraint(sum(int(coefficient_list[v])*x[v] for v in I) == -inhomogeneous_term)
		else:
			# In case of strict or non strict inequality we just define a non strict constraint
			# for the MIP program since only strict constraints are allowed.
			p.add_constraint(sum(int(coefficient_list[v])*x[v] for v in I) >= -inhomogeneous_term)

	p.show()
	optimal_value = p.solve()
	print('optimal_value =',optimal_value)
	print('optimal_value type =', type(optimal_value))

	return optimal_value



#----------------------------------------------------------------------------------------------#
def unit_boundary_ball(dim):
	
	""" Computes the half unitary boundary ball, where the fist half coordinates have infinity norm equal or smaller than one. """

	halfdim = dim//2

	boundary_list_neg = []
	boundary_list_pos = []
	
	for i in range(halfdim):
		
		unit_boundary_neg = NNC_Polyhedron(dim,'universe')
		unit_boundary_neg.add_constraint(Variable(i) == -1)
		unit_boundary_pos = NNC_Polyhedron(dim,'universe')
		unit_boundary_pos.add_constraint(Variable(i) == 1)

		for j in range(halfdim):
			if j!=i:
				unit_boundary_neg.add_constraint(Variable(j) >= -1)
				unit_boundary_neg.add_constraint(Variable(j) <= 1)
				unit_boundary_pos.add_constraint(Variable(j) >= -1)
				unit_boundary_pos.add_constraint(Variable(j) <= 1)
		
		boundary_list_neg.append(NNC_Polyhedron(unit_boundary_neg))
		boundary_list_pos.append(NNC_Polyhedron(unit_boundary_pos))

	return boundary_list_neg,boundary_list_pos



#----------------------------------------------------------------------------------------------#
def intersection(poly,poly_list_neg,poly_list_pos):

	""" Returns the list of polyhedra intersections between a polyhedron and a list of polyhedra. """

	int_poly_list_neg = []
	int_poly_list_pos = []
	
	for p in poly_list_neg:
	
		int_poly = NNC_Polyhedron(poly)
		print('Before intersection rel_unit_poly is empty =',int_poly.is_empty())
		print('affine dimension =', int_poly.affine_dimension())
		int_poly.intersection_assign(p)
		print('int_poly =',int_poly.constraints())
		if not int_poly.is_empty():
			int_poly_list_neg.append(int_poly)

	for p in poly_list_pos:
		
		int_poly = NNC_Polyhedron(poly)
		print('Before intersection rel_unit_poly is empty =',int_poly.is_empty())
		print('affine dimension =', int_poly.affine_dimension())
		int_poly.intersection_assign(p)
		print('int_poly =',int_poly.constraints())
		if not int_poly.is_empty():
			int_poly_list_pos.append(int_poly)

	if not int_poly_list_neg and not int_poly_list_pos: print('INTERSECTION WITH THE UNITARY BOUNDARY BALL IS EMPTY')

	return int_poly_list_neg,int_poly_list_pos




#----------------------------------------------------------------------------------------------#
def max_scaling(poly,coord):

	""" Obtain the maximum scaling for a relation unit boundary polyhedron. """
	
	dim = poly.space_dimension()
	halfdim = dim//2
	new_coord = coord + halfdim
	
	max_scaling = -1
	sol_max_dict = poly.maximize(1*Variable(new_coord))
	print('    sol_max_dict=',sol_max_dict)
	if sol_max_dict['bounded'] == False:
		print('EXPLOSION WAS NOT DETECTED')
		sys.exit()
	else:
		max_value = float(sol_max_dict['sup_n']/sol_max_dict['sup_d'])
        
	sol_min_dict = poly.minimize(1*Variable(new_coord))
	print('    sol_min_dict=',sol_min_dict)
	if sol_min_dict['bounded'] == False:
		print('EXPLOSION WAS NOT DETECTED')
		sys.exit()
	else:
		min_value = float(sol_min_dict['inf_n']/sol_min_dict['inf_d'])
		
	scaling = max(abs(max_value),abs(min_value))
		
	if scaling > max_scaling:
		max_scaling = scaling

	return max_scaling



#----------------------------------------------------------------------------------------------#
def max_scaling_list(poly_list):

	""" Obtain the maximum scaling for the list of unit boundary polyhedra. """
	scaling_list = [-1]
	i=0
	for poly in poly_list:
		scaling = max_scaling(poly,i)
		print('scaling for poly ',poly.constraints(), ' is ',scaling)
		scaling_list.append(scaling)
		i += 1
	
	return max(scaling_list)



#----------------------------------------------------------------------------------------------#
def max_poly_optimization(relpoly):

	""" Obtains the maximum absolute value of the second half part of coordinates in the polyhedron
		relation having the first half part of coordinates with infinite norm equal to one.
		input:	relpoly				NNC_Polyhedron
		output:	max_scaling			float. """

	dim = relpoly.space_dimension()
	halfdim = dim//2
	#print('***************** max_poly_optimization ******************')
	#print(relpoly)
	#print('relpoly =',relpoly.constraints())
	""" Computes the half unitary ball, where the first half coordinates have infinity norm equal
		or smaller than one. """
	unit_ball = NNC_Polyhedron(dim,'universe')
	for i in range(halfdim):
		unit_ball.add_constraint(Variable(i) >= -1)
		unit_ball.add_constraint(Variable(i) <= 1)

	#print(unit_ball)
	#print('unit_ball=',unit_ball.constraints())
	""" Intersection of the relation polyhedron and the half unitary ball. """
	rel_unit_poly = NNC_Polyhedron(relpoly)
	#print('Before intersection rel_unit_poly is empty =',rel_unit_poly.is_empty())
	#print('affine dimension =', rel_unit_poly.affine_dimension())
	rel_unit_poly.intersection_assign(unit_ball)

	if rel_unit_poly.is_empty(): print('INTERSECTION WITH THE UNITARY BALL IS EMPTY =')
	#print(rel_unit_poly)
	#print('rel_unit_poly=',rel_unit_poly.constraints())

	max_scaling = -1
	for i in range(halfdim,dim):

		#print('    coordinate ',i)
		proj_poly = pplf.ppl_functions.projection(rel_unit_poly,[i])
		#print('    proj_poly=',proj_poly.constraints())
		sol_max_dict = proj_poly.maximize(1*Variable(i))
		if sol_max_dict['bounded'] == False:
			print('EXPLOSION WAS NOT DETECTED')
			sys.exit()
		else:
			#print('    sol_max_dict=',sol_max_dict)
			max_value = float(sol_max_dict['sup_n']/sol_max_dict['sup_d'])

		sol_min_dict = proj_poly.minimize(1*Variable(i))
		if sol_min_dict['bounded'] == False:
			print('EXPLOSION WAS NOT DETECTED')
			sys.exit()
		else:
			
			#print('    sol_min_dict=',sol_min_dict)
			min_value = float(sol_min_dict['inf_n']/sol_min_dict['inf_d'])

		scaling = max(abs(max_value),abs(min_value))

		if scaling > max_scaling:
			max_scaling = scaling

	return max_scaling


#----------------------------------------------------------------------------------------------#
def max_poly_optimization_v2(relpoly):
	
	""" Obtains the maximum absolute value of the second half part of coordinates in the polyhedron
		relation having the first half part of coordinates with infinite norm equal to one.
		input:	relpoly				NNC_Polyhedron
		output:	max_scaling			float. """
	
	dim = relpoly.space_dimension()

	""" Computes the list of half unitary boundary ball. """
	unit_boundary_ball_list_neg, unit_boundary_ball_list_pos = unit_boundary_ball(dim)

	""" List of intersection of the relation polyhedron and the half unitary boundary ball. """
	intersection_poly_list_neg,intersection_poly_list_pos = intersection(relpoly,unit_boundary_ball_list_neg,unit_boundary_ball_list_pos)
	
	""" Compute the maximum scaling for each of the intersected polyhedra in the list. """
	maximum_scaling_neg = max_scaling_list(intersection_poly_list_neg)
	maximum_scaling_pos = max_scaling_list(intersection_poly_list_pos)
	maximum_scaling = max(maximum_scaling_neg,maximum_scaling_pos)

	if not intersection_poly_list_neg and not intersection_poly_list_pos: print('INTERSECTION WITH THE UNITARY BOUNDARY BALL IS EMPTY\n')
	
	
	return maximum_scaling


#----------------------------------------------------------------------------------------------#
def max_optimization(relpoly):

	""" Obtains the maximum absolute value of the second half part of coordinates in the polyhedron 
	relation having the first half part of coordinates with infinite norm equal to one. 
	input:	relpoly				NNC_Polyhedron
	output:	max_scaling			float. """

	dim = relpoly.space_dimension()
	halfdim = dim//2
	
	""" Computes the half unitary ball, where the first half coordinates have infinity norm equal 
	or smaller than one. """
	unit_ball = NNC_Polyhedron(dim,'universe')
	for i in range(halfdim):
		unit_ball.add_constraint(Variable(i) >= -1)
		unit_ball.add_constraint(Variable(i) <= 1)
	
	""" Intersection of the relation polyhedron and the half unitary ball. """
	rel_unit_poly = NNC_Polyhedron(relpoly)
	rel_unit_poly.intersection_assign(unit_ball)

	max_scaling = -1
	for i in range(halfdim,dim):
			
			r = -1
			scaling = optimization(rel_unit_poly,r,i)
			max_scaling = max(max_scaling,scaling)

			r = 1
			scaling = optimization(rel_unit_poly,r,i)
			max_scaling = max(max_scaling,scaling)


	return max_scaling



#----------------------------------------------------------------------------------- 03/11/2016 ---#
def max_optimization_MIP(relpoly):
	
	""" Obtains the maximum absolute value of the second half part of coordinates in the polyhedron
		relation having the first half part of coordinates with infinite norm equal to one.
		input:	relpoly				NNC_Polyhedron
		output:	max_scaling			float. """
	
	dim = relpoly.space_dimension()
	halfdim = dim//2
	
	""" Computes the half unitary ball, where the first half coordinates have infinity norm equal
		or smaller than one. """
	unit_ball = NNC_Polyhedron(dim,'universe')
	for i in range(halfdim):
		unit_ball.add_constraint(Variable(i) >= -1)
		unit_ball.add_constraint(Variable(i) <= 1)
	
	""" Intersection of the relation polyhedron and the half unitary ball. """
	rel_unit_poly = NNC_Polyhedron(relpoly)
	rel_unit_poly.intersection_assign(unit_ball)
	
	max_scaling = -1
	for i in range(halfdim,dim):
		
		r = -1
		scaling = optimization_MIP(rel_unit_poly,r,i)
		max_scaling = max(max_scaling,scaling)
			
		r = 1
		scaling = optimization_MIP(rel_unit_poly,r,i)
		max_scaling = max(max_scaling,scaling)


	return max_scaling




#----------------------------------------------------------------------------------------------#
def optimization_set(init_rel,phi_rel_list,final_rel,opt_solver):
	
	""" Computes the maximum scaling by considering all the possible compositions among initial 
	relation polyhedron, phi relation polyhedron and final relation polyhedron. 
	input:	init_rel			ppl.NNC_Polyhedron
			phi_rel_list		ppl.NNC_Polyhedron list
			final_rel			ppl.NNC_Polyhdefon
	output:	max_scaling			float. """

	opt_set_time = time.time()
	
	max_scaling = -1
	dim = init_rel.space_dimension()
	max_relpoly = NNC_Polyhedron(dim,'empty')
	
	for phi_rel in phi_rel_list:

		#print('initial rel=',init_rel.constraints())
		relpoly = pplf.relation_reach.composition_rel(init_rel,phi_rel)
		#print('phi_rel=',phi_rel.constraints())
		#print('relpoly after phi_rel composition=',relpoly.constraints())
		relpoly = pplf.relation_reach.composition_rel(relpoly,final_rel)
		#print('final rel=',final_rel.constraints())
		#print('final relpoly=',relpoly.constraints())
		#print('relpoly.space_dimension=',relpoly.space_dimension())
		#print('relpoly.affine_dimension=',relpoly.affine_dimension())

		#print('relpoly is empty =',relpoly.is_empty())
		if not relpoly.is_empty():
			
			if opt_solver == 1:
				scaling = max_optimization(relpoly)			#<--- THIS IS OPTIMIZING WITH GLPK SOLVER, BUT WE CAN SET DIFFERENT SOLVERS
			else:
				scaling = max_optimization_MIP(relpoly)	#<--- THIS IS ALSO WORKING WELL, BUT WITH PPL SOLVER  (in this case, opt_solver = 2)

			if scaling > max_scaling:
				max_scaling = scaling
				max_relpoly = relpoly

	opt_set_time = time.time() - opt_set_time
				
	return max_scaling,max_relpoly,opt_set_time

