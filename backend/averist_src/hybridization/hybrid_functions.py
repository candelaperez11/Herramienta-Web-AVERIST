from sage.numerical.mip import *
from sage.modules.free_module_element import vector
from ppl import Variable, Linear_Expression
from numpy import array, linalg
from fractions import Fraction
from math import gcd
from functools import reduce
import subprocess as sp
import sys



#----------------------------------------------------------------------------------------------#
def maximize(dyn_poly,indx,indy,indobj,signx,signy):
	
	dim = dyn_poly.space_dimension()

	# Set the Linear Programming problem
	p=MixedIntegerLinearProgram(maximization=True,solver="GLPK")

	# Define the variables
	x = p.new_variable(real=True)
	for i in range(dim):
		x[i]
	
	y = p.new_variable(real=True)
	for i in range(dim):
		y[i]

	# Set the objective function
	p.set_objective(x[indobj] - y[indobj])

	# Set the constraints ||x||,||y|| = 1
	for ind in range(dim):
		
		if ind == indx:
			p.add_constraint(x[ind] == signx)
		else:
			p.add_constraint(x[ind] >= -1)
			p.add_constraint(x[ind] <= 1)
		p.set_min(x[ind], None)
		
		if ind == indy:
			p.add_constraint(y[ind] == signy)
		else:
			p.add_constraint(y[ind] >= -1)
			p.add_constraint(y[ind] <= 1)
		p.set_min(y[ind], None)


	# Set the constraints x,y in dyn_poly
	for poly_constraint in dyn_poly.constraints():
		
		coeffs = poly_constraint.coefficients()
		term = poly_constraint.inhomogeneous_term()
		type = poly_constraint.type()
		
		constraintx = 0
		constrainty = 0
		for i in range(dim):
			constraintx = constraintx + coeffs[i]*x[i]
			constrainty = constrainty + coeffs[i]*y[i]
		
		if type == 'equality':
			constraintx = constraintx + term == 0
			constrainty = constrainty + term == 0
		elif type == 'nonstrict_inequality':
			constraintx = constraintx + term >= 0
			constrainty = constrainty + term >= 0
		elif type == 'strict_inequality':
			constraintx = constraintx + term > 0
			constrainty = constrainty + term > 0
		
		p.add_constraint(constraintx)
		p.add_constraint(constrainty)



	try:
		max = p.solve()
	except RuntimeError:
		except_value = str(sys.exc_info()[1])

		if except_value == "'GLPK : Solution is undefined'":
			max = 0.0
		elif except_value == "'GLPK : There is no feasible integer solution to this Linear Program'":
			max = 0.0
		else:
			raise Exception(except_value)
	

	x = p.get_values(x)
	y = p.get_values(y)


	return max,x,y



#----------------------------------------------------------------------------------------------#
def minimize(dyn_poly,indx,indy,indobj,signx,signy):

	dim = dyn_poly.space_dimension()
	
	# Set the Linear Programming problem
	p=MixedIntegerLinearProgram(maximization=False,solver="GLPK")
	
	# Define the variables
	x = p.new_variable(real=True)
	#x = p.new_variable(integer=True)
	for i in range(dim):
		x[i]
	
	y = p.new_variable(real=True)
	#y = p.new_variable(integer=True)
	for i in range(dim):
		y[i]
	
	# Set the objective function
	p.set_objective(x[indobj] - y[indobj])
	
	# Set the constraints ||x||,||y|| = 1
	for ind in range(dim):
		
		if ind == indx:
			p.add_constraint(x[ind] == signx)
		else:
			p.add_constraint(x[ind] >= -1)
			p.add_constraint(x[ind] <= 1)
		p.set_min(x[ind], None)
		
		if ind == indy:
			p.add_constraint(y[ind] == signy)
		else:
			p.add_constraint(y[ind] >= -1)
			p.add_constraint(y[ind] <= 1)
		p.set_min(y[ind], None)

		
	# Set the constraints x,y in dyn_poly
	for poly_constraint in dyn_poly.constraints():
		
		coeffs = poly_constraint.coefficients()
		term = poly_constraint.inhomogeneous_term()
		type = poly_constraint.type()
			
		constraintx = 0
		constrainty = 0
		for i in range(dim):
			constraintx = constraintx + coeffs[i]*x[i]
			constrainty = constrainty + coeffs[i]*y[i]

		if type == 'equality':
			constraintx = constraintx + term == 0
			constrainty = constrainty + term == 0
		elif type == 'nonstrict_inequality':
			constraintx = constraintx + term >= 0
			constrainty = constrainty + term >= 0
		elif type == 'strict_inequality':
			constraintx = constraintx + term > 0
			constrainty = constrainty + term > 0
			
		p.add_constraint(constraintx)
		p.add_constraint(constrainty)

#	p.show()

	try:
		min = p.solve()
	except RuntimeError:
		except_value = str(sys.exc_info()[1])
		if except_value == "'GLPK : Solution is undefined'":
			min = 0.0
		elif except_value == "'GLPK : There is no feasible integer solution to this Linear Program'":
			min = 0.0
		else:
			raise Exception(except_value)

	x = p.get_values(x)
	y = p.get_values(y)

	return min,x,y



#----------------------------------------------------------------------------------------------#
def optimize_norm(dyn_poly,indx,indy,indobj,signx,signy):
	
	max_value,xmax,ymax = maximize(dyn_poly,indx,indy,indobj,signx,signy)

	min_value,xmin,ymin = minimize(dyn_poly,indx,indy,indobj,signx,signy)


	abs_max_value = abs(max_value)
	abs_min_value = abs(min_value)
	
	if abs_max_value >= abs_min_value:
		
		opt_value = abs_max_value
		xopt = xmax
		yopt = ymax
	
	else:
		
		opt_value = abs_min_value
		xopt = xmin
		yopt = ymin
	
	return opt_value,xopt,yopt



#----------------------------------------------------------------------------------------------#
def optimal_distance(dyn_poly):

	dim = dyn_poly.space_dimension()
	sign_list = [-1,1]
	opt_value = 0.0
	xopt = 0.0
	yopt = 0.0
	
	for indobj in range(dim):
		for indx in range(dim):
			for indy in range(dim):
				for signx in sign_list:
					for signy in sign_list:
						

						opt_value_norm,xopt_norm,yopt_norm = optimize_norm(dyn_poly,indx,indy,indobj,signx,signy)
						

						if opt_value_norm > opt_value:
							opt_value = opt_value_norm
							xopt = xopt_norm
							yopt = yopt_norm

	return opt_value,xopt,yopt



#----------------------------------------------------------------------------------------------#
def mid_point(xdict,ydict):

	x = vector(xdict.values())
	y = vector(ydict.values())

	midpoint = (x+y)/2

	return midpoint



#----------------------------------------------------------------------------------------------#
def str2array(str_exp,var_dict,inv_var_dict):

	""" Transforms a dynamical string expression into a matrix.
		-----------------------------------------------------------------------
		input:	str_exp			'dx==yANDdy==-1*x'			string
				var_dict		{'x':0, 'y':1}              dictionary
				inv_var_dict    {0:'x', 1:'y'}              dictionary
		output: A				array([[ 0,  1],[-3,  1]])	numpy.array """

	expression_list = str_exp.split('AND')
	
	dim = len(inv_var_dict)
	# Define the variables
	for i in range(dim):
		var_str = inv_var_dict[i] + ' = Variable('+ str(i) +')'
		exec(var_str)

	# Define null expression to include all coefficients in the linear expression
	null_expression = ''
	for i in range(dim):
		null_expression += '+0*' + str(inv_var_dict[i])

	# Construct the matrix by getting the coefficients of every linear expression
	array_list = [0]*dim
	for expression in expression_list:
		term_list = expression.split('==')
		for term in term_list:
			if 'd' in term:
				term = term.replace('d','')
				array_index = var_dict[term]
			else:
				le_exec = 'Linear_Expression('+ term + null_expression + ')'
				le = eval(le_exec)
			
		array_list[array_index] = array(le.coefficients())




	A = array(array_list)

	return A



#----------------------------------------------------------------------------------------------#
def lcm(numbers):
	
	""" Get the least common multiple of a list of numbers
		-------------------------------------------------------------------------------
		input: 	numbers		[1,2,6]		list of integers
		output:				6			integer """

	return reduce(lambda x, y: (x*y)//gcd(x,y), numbers, 1)



#----------------------------------------------------------------------------------------------#
def proportional_integer_vector(v):
	
	""" Computes a proportional vector with integer values from one with rational
		values.
		-------------------------------------------------------------------------------
		input:	v	[Fraction(1, 3), Fraction(1, 2)]	numpy.array
		output:	pv	[2,3]								list of integer """
		
	
	# Determine the list for numerators and denominators
	numerator_list = []
	denominator_list = []
	
	for value in v:
		numerator_list.append(value.numerator)
		denominator_list.append(value.denominator)

	# Least common multiple of the denominators
	least_cm = lcm(denominator_list)
	
	integer_list = [int(least_cm*a/b) for a,b in zip(numerator_list,denominator_list)]

	# Divide every integer by the greatest common divisor to obtain the smallest possible values
	GCD = reduce(gcd,integer_list)
	for i in range(len(integer_list)):
		integer_list[i] = integer_list[i]//GCD

	return integer_list



#----------------------------------------------------------------------------------------------#
def solve_linear_system(A,b):

	""" Solves the linear system Ax = b where x is the unknown. """

	x = linalg.solve(A,b)

	return x



#----------------------------------------------------------------------------------------------#
def solve_linear_system_integer(A,b):

	""" Solves the linear system Ax = b where x is the unknown and returns a proportional x
		value with integer coefficients. """

	x = linalg.solve(A,b)
	print('solution =',x)

	rationalx = []
	for value in x:
		rationalx.append(Fraction(value))
	print('rational solution =',rationalx)

	integerx = proportional_integer_vector(rationalx)
	print('integer solution =',integerx)

	return integerx



#----------------------------------------------------------------------------------------------#
def real2integer(real_array):
	
	""" Given a list of reals it returns a list of integers. """
	
	rational = []
	for value in real_array:
		rational.append(Fraction(value))
	print('rational solution =',rational)

	integer = proportional_integer_vector(rational)
	print('integer solution =',integer)
	
	return integer



#----------------------------------------------------------------------------------------------#
def positive_first_coefficient(coefficient_array):

	for i in range(len(coefficient_array)):

		if coefficient_array[i] < 0.0:
			return -1 * coefficient_array
		elif coefficient_array[i] > 0.0:
			return coefficient_array



#################################################################################
# Get the numerator and denominator from a coefficient and the variable of an	#
# expression																	#
#-------------------------------------------------------------------------------#
# input: 	expression	'3/2x'													#
#			var_dict	{'x':0,'y':1}											#
#																				#
# output:	num		3															#
#			den		2															#
#			var		'x'															#
#################################################################################
def get_coefficient(expression,var_dict):

	num = None
	den = None
	variable = None

	for i in var_dict:

		if i in expression:

			exp = expression.split('*'+i)
			coeff_str = exp[0]

			if coeff_str == i:
				num = 1
				den = 1
			else:
				fraction = coeff_str.split('/')
				num = int(fraction[0])
				if len(fraction) == 1:
					den = 1
				else:
					den = int(fraction[1])

			variable = i

	if variable is None:
		# No aparece ninguna variable de estado: es el término constante/afín
		# de una dinámica como 'dx==-1' (variable=None indica al llamador que
		# este valor es el término independiente, no el coeficiente de una
		# variable).
		fraction = expression.split('/')
		num = int(fraction[0])
		den = int(fraction[1]) if len(fraction) > 1 else 1

	return num,den,variable



#################################################################################
# Get the coefficients from an expression got from splitting plus				#
#################################################################################
def get_coeff_minus(expression,num_list,den_list,var_list,var_dict,constant):

	exp_minus = expression.split('-')
	for em in exp_minus:

		if (exp_minus.index(em) == 0):
			sign = 1
		else:
			sign = -1

		if (em != ''):
			num,den,var = get_coefficient(em,var_dict)
			if var is None:
				constant += sign * Fraction(num,den)
			else:
				num_list[var_dict[var]] = num * sign
				den_list[var_dict[var]] = den
				var_list.append(var)

	return num_list,den_list,var_list,constant



#################################################################################
# Get the least common multiple of a list of numbers							#
#-------------------------------------------------------------------------------#
# input: 	numbers		(1,2,6)													#
#																				#
# output:			6															#
#################################################################################
def lcm(numbers):
	return reduce(lambda x, y: (x*y)//gcd(x,y), numbers, 1)


#################################################################################
# Get the coefficients from an expression										#
# expression = '-2/3y+z+3t-1/6r+l-x'											#
# var_list = {'x':0,'y':1,'z':2,'t':3,'r':4,'l':5,'v':6}						#
# return (-6,-4,6,18,-1,6,0)													#
#################################################################################
def get_coefficients(expression,var_dict):

	# Determine the list for the coefficients
	n_coeff = len(var_dict)
	num_list = [0]*n_coeff
	den_list = [1]*n_coeff

	var_list = []

	# Término constante/afín de la expresión (p.ej. el '-1' de 'dx==-1');
	# se acumula aparte porque no tiene una variable de estado asociada.
	constant = Fraction(0)

	first_negative = False

	# Split considering the +
	exp_plus = expression.split('+')

	# Split considering the -
	for ep in exp_plus:
		if (len(ep.split('-')) == 1):
			num,den,var = get_coefficient(ep,var_dict)
			if var is None:
				constant += Fraction(num,den)
			else:
				num_list[var_dict[var]] = num
				den_list[var_dict[var]] = den
				var_list.append(var)
		else:
			num_list,den_list,var_list,constant = get_coeff_minus(ep,num_list,den_list,var_list,var_dict,constant)

	# Least common multiple of the denominators (incluyendo el denominador
	# del término constante, para que quede escalado de forma consistente
	# con el resto de coeficientes)
	least_cm = lcm(den_list + [constant.denominator])

	coeff_list = [least_cm*a//b for a,b in zip(num_list,den_list)]
	constant_scaled = int(constant * least_cm)

	return coeff_list,constant_scaled



#################################################################################
# Get the coefficients, symbols and constant of a simple expression				#
# 'x+y>=3' ---------> ([1,1],'>=',2)											#
#################################################################################
def simple_expression(expression,var_dict):
	
	#coeffs_sym = []		# for storing the coefficients and the symbols of the complement expressions
	
	if '=' in expression:
		if '>=' in expression:
			parts = expression.split('>=')
			symbol = '>='
		elif '<=' in expression:
			parts = expression.split('<=')
			symbol = '<='
		else:
			parts = expression.split('==')
			symbol = '='

	else:
		if '>' in expression:
			parts = expression.split('>')
			symbol = '>'
		elif '<' in expression:
			parts = expression.split('<')
			symbol = '<'


	coeff_list,constant = get_coefficients(parts[1],var_dict)
	coeffs_sym =[coeff_list,symbol,parts[0],constant]

	return coeffs_sym



#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 15/03/2016 ---#
def dynamics_string_to_list(str_exp,inv_var_dict,var_dict):
	
	"""
		Generates a polyhedron from a string with the linear constraints determining.
		input:	str_exp			string					'dx==10*yANDdy==-1*x' or 'dx+dy>0'
		inv_var_dict	dict					{0: 'x', 1: 'y'}
		
		output: poly			ppl.NNC_Polyhedron. """
	
	# state space dimension
	dim = len(inv_var_dict)
	
	# Define variables (the first half have the names in the inv_var_dict, while the second
	# half set of variables have no name)
	#instr = ''
	for i in inv_var_dict:
		
		dstr = 'd' + str(inv_var_dict[i])
		dstr = ''.join(dstr.split())
		vstr = 'x'+ str(i+dim)
		vstr = ''.join(vstr.split())
		str_exp = str_exp.replace(dstr,vstr)
	
	
	dynamics_expression_list = []
	if str_exp != 'True':
		
		#print 'str_exp =', str_exp
		expr = str_exp.split('AND')		# Assumption: there are no OR expressions
		#print 'expr =',expr
		for e in expr:
			e = ''.join(e.split())
			se = simple_expression(e,var_dict)
			dynamics_expression_list.append(se)
	#print 'poly =',poly.constraints()

	return dynamics_expression_list



#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 15/03/2016 ---#
def smt_trans_constraint(constraint):
	
	""" Translates a PPL constraint to an SMT-lib constraint. """
	
	coefflist = constraint.coefficients()
	
	strsymbol = constraint.type()
	if strsymbol == 'equality':
		symbol = '='
	elif strsymbol == 'strict_inequality':
		symbol = '>'
	else:
		symbol = '>='
	
	term = - constraint.inhomogeneous_term()


	strconst = ' (' + symbol + ' (+'
	
	for i in range(len(coefflist)):
		strconst += '(* ' + str(coefflist[i]) + ' x' + str(i) + ')'

	strconst += ') ' + str(term) + ')\n'
	
	return strconst



#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 15/03/2016 ---#
def polyhedron_to_smt(poly):
	
	""" Given a PPL polyhedron, it outputs the smt string for a point belonging to the polyhedron. """
	
	strsmt = ''
	
	constraint_system = poly.constraints()
	for constraint in constraint_system:
		strsmt += smt_trans_constraint(constraint)
	
	return strsmt



#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 15/03/2016 ---#
def smt_trans_constraint_given_variables(constraint,variable_list):
	
	""" Translates a PPL constraint to an SMT-lib constraint. """
	
	coefflist = constraint.coefficients()
	
	strsymbol = constraint.type()
	if strsymbol == 'equality':
		symbol = '='
	elif strsymbol == 'strict_inequality':
		symbol = '>'
	else:
		symbol = '>='
	
	term = - constraint.inhomogeneous_term()


	strconst = ' (' + symbol + ' (+'
	
	for i in range(len(coefflist)):
		strconst += '(* ' + str(coefflist[i]) + variable_list[i] + ')'

	strconst += ') ' + str(term) + ')\n'
	
	return strconst




#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 15/03/2016 ---#
def polyhedron_to_smt_given_variables(poly,variable_list):
	
	""" Given a PPL polyhedron, it outputs the smt string for a point belonging to the polyhedron. """
	
	strsmt = ''
	
	constraint_system = poly.constraints()
	for constraint in constraint_system:
		strsmt += smt_trans_constraint_given_variables(constraint,variable_list)
	
	return strsmt



#----------------------------------------------------------------------------------------------#
def run_smt(smt_string,output):
	
	""" Given an SMT-lib satisfiability problem and output folder, runs it to check the answer. """
	
	f = open(output+'/sat.smt','w')
	
	f.write(smt_string)
	f.close()
	
	sp.call(['sh','smt.sh',output+'/sat.smt',output+'/sol_sat.smt'])
	
	sol = open(output+'/sol_sat.smt','r')
	l= sol.readline()
#	print 'solution =', l
	l = l.strip()
	sol.close()
	
	if l=='sat': return True
	else: return False



#----------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------- 08/03/2016 ---#
def smt_transition_question(initial_element,final_element,dynamics_string,inv_var_dict,var_dict,namefolder):
	
	output = namefolder + '/output'
	
	transition_question_string = ''
	""" Declare the variables as real values """
	dim = initial_element.space_dimension()
	
	
	transition_question_string += '(assert (exists ('
	for i in range(dim):
		transition_question_string += ' (x'+str(i)+' Real)'
	transition_question_string += ' (t Real) )\n'

	transition_question_string += '(and (> t 0.0)\n'
	# variables different from zero all together
	variable_different = '(or'
	for i in range(dim):
		variable_different += ' (< x'+str(i)+' 0.0)(> x'+str(i)+' 0.0)'

	variable_different += ')\n'
	
	transition_question_string += variable_different
	
	transition_question_string += polyhedron_to_smt(initial_element)
	
	# Determine x + Ax + b as the new variables (b = affine/constant term,
	# e.g. the '-1' in 'dx==-1'; 0 for purely homogeneous dynamics)
	dynamics_list = dynamics_string_to_list(dynamics_string,inv_var_dict,var_dict)

	new_variable_list = []

	for i in range(dim):

		for dynamics in dynamics_list:

			if dynamics[2] == 'x'+str(i+dim):
				coefficient_list = dynamics[0]
				constant_term = dynamics[3]

		new_variable = '(+ x'+str(i)

		for j in range(len(coefficient_list)):

			coefficient = coefficient_list[j]
			new_variable += '(* ' + str(coefficient) + ' x'+ str(j) + ' t)'

		if constant_term:
			new_variable += '(* ' + str(constant_term) + ' t)'

		new_variable += ')'
	
		new_variable_list.append(new_variable)
	
	transition_question_string += polyhedron_to_smt_given_variables(final_element,new_variable_list)
	
	transition_question_string += ')))\n'
	transition_question_string += '(check-sat)\n'
	
#	print transition_question_string
	
	return run_smt(transition_question_string,output)


