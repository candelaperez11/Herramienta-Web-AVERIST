from ppl import *
import subprocess as sp


#----------------------------------------------------------------------------------------------#
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


	strconst = '(assert (' + symbol + ' (+'

	for i in range(len(coefflist)):
		strconst += '(* ' + str(coefflist[i]) + ' x' + str(i) + ')'

	strconst += ') ' + str(term) + '))\n'

	return strconst

	

#----------------------------------------------------------------------------------------------#
def smt_trans_relpoly(relpoly,alpha_restricted):
	
	""" Translates a PPL relation polyhedron to an SMT-lib satisfiability problem. """

	strsmt = ''
	# Declare the variables as real values (just the first half part of the variables)
	dim = relpoly.space_dimension()
	
	for i in range(dim):
		strsmt += '(declare-fun x'+str(i)+' () Real)\n'
	
	# Declare alpha
	strsmt += '(declare-fun a () Real)\n'
	# If alpha is restricted define the constraint
	if alpha_restricted:
		strsmt += '(assert (> a 1))\n'

	# Define the constraints in the relpoly
	cs = relpoly.constraints()
	for c in cs:
			strsmt += smt_trans_constraint(c)


	# Define the constraints for x' = ax
	halfdim = dim//2
	for i in range(halfdim):
		strsmt += '(assert (= x' + str(i+halfdim) + '(* a x' + str(i) + ')))\n'


	strsmt += '(check-sat)\n'


	return strsmt





#----------------------------------------------------------------------------------------------#
def run_smt(smt_string,output):
	
	""" Given an SMT-lib satisfiability problem and output folder, runs it to check the answer. """

	f = open(output+'/smt/sat.smt','w')

	f.write(smt_string)
	f.close()
	
	sp.call(['sh','smt.sh',output+'/smt/sat.smt',output+'/smt/sol_sat.smt'])
	
	sol = open(output+'/smt/sol_sat.smt','r')
	l= sol.readline()
	print('solution =', l)
	l = l.strip()
	sol.close()
	
	if l=='sat': return True
	else: return False


