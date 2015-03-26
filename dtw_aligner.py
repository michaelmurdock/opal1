# dtw_aligner.py
#
# This DTW alignment algorithm is based on a code snippet from here:
# http://jeremykun.com/2012/07/25/dynamic-time-warping/


from __future__ import print_function
import math
import sys
import logging


import utilsLib
import cost_info as ci
import origin_points


bVerbose_mode = True

class dtw_aligner(object):
	'''
	An instance of this class is used to align two sequences of COriginPoint objects. 
	For convenience we use the COriginPointsList class to hold each sequence, since this class encapsulates the MDAT reading functionality.
	'''
	def __init__(self, xorigin_points, xestimate_points, bverbose_mode, bprint_to_screen):
		'''
		Original Code:
		Constructor requires two sequences, the first is a list of corigin_point instances,
		the second is a list of cestimate_point instances.
		'''
		self._bverbose_mode = bverbose_mode
		self._bprint_to_screen = bprint_to_screen

		self._Q = xorigin_points
		self._P = xestimate_points

		# Save away the dimensions of the cost and choice matrices, which are based on the sizes of Q and P
		self._numRows = len(self._Q)
		self._numCols = len(self._P)

	def create_empty_cost_matrix(self):
		'''
		'''
		# create the cost matrix, all with zero costs
		self._cost = [[0 for _ in range(self._numCols)] for _ in range(self._numRows)]
		return utilsLib.Result(True,message='', item=None)

	def create_empty_cost_info_matrix(self):
		'''
		'''
		# create the cost_info_matrix, all with placeholder cost_info objects
		self._cost_info_matrix = [[ci.cost_info(row, col) for col in range(self._numCols)] for row in range(self._numRows)]
		return utilsLib.Result(True,message='', item=None)
		

	def _distance(self, p1, p2):
		'''
		Private method that takes two CPoint instances, which are (x, y) coordinates, 
		p1 and p2, and returns the (Euclidean) distance.
		'''
		d = math.sqrt(math.pow((p1.x - p2.x), 2.0) + math.pow((p1.y - p2.y), 2.0))
		return d


	def compute_cost(self):
		'''
		Calling this method causes the full alignment cost matrix to be computed.
		Before this method can be called, the client must first call th ecreate_empty_cost_matrix() and create_empty_choices_matrix() methods.
		'''

		# compute the cost for [0][0] for the _cost matrix and the _cost_info_matrix
		local_cost = self._distance(self._Q[0], self._P[0])
		self._cost[0][0] = local_cost
		self._cost_info_matrix[0][0].accum_cost = local_cost

		
		# initialize the first COLUMN
		for i in xrange(1, self._numRows):

			# Everything related to the _cost object
			prev_accum_cost = self._cost[i-1][0]
			curr_local_cost = self._distance(self._Q[i], self._P[0])
			self._cost[i][0] = prev_accum_cost + curr_local_cost
			
			# Everything related to the _cost_info_matrix
			prev_cost_info_instance = self._cost_info_matrix[i-1][0]
		

			# Create a new cost_info instance for this current position, and then add to it the previous cost_info instance
			cost_info_instance = ci.cost_info(i,0,local_cost=curr_local_cost)
			cost_info_instance.add_info_from_prev_cost_info_instance(prev_cost_info_instance.row, 
																	 prev_cost_info_instance.col, 
																	 prev_cost_info_instance.local_cost,
																	 prev_cost_info_instance.accum_cost)

			# New: This is where I think we are required to manually compute the the current accum cost
			cost_info_instance.accum_cost = cost_info_instance.local_cost + cost_info_instance.prev_accum_cost

			# Save away this cost_info object 
			self._cost_info_matrix[i][0] = cost_info_instance

		# initialize the first ROW
		for j in xrange(1, self._numCols):

			# Everything related to the _cost object
			prev_accum_cost = self._cost[0][j-1]
			curr_local_cost = self._distance(self._Q[0], self._P[j])
			self._cost[0][j] = prev_accum_cost + curr_local_cost

			# Everything related to the _cost_info_matrix
			prev_cost_info_instance = self._cost_info_matrix[0][j-1]

			# Create a new cost_info instance for this current position, and then add to it the previous cost_info instance
			cost_info_instance = ci.cost_info(0, j, local_cost=curr_local_cost)
			cost_info_instance.add_info_from_prev_cost_info_instance(prev_cost_info_instance.row, 
																	 prev_cost_info_instance.col, 
																	 prev_cost_info_instance.local_cost,
																	 prev_cost_info_instance.accum_cost)

			# New: This is where I think we are required to manually compute the the current accum cost
			cost_info_instance.accum_cost = cost_info_instance.local_cost + cost_info_instance.prev_accum_cost

			# Save away this cost_info object 
			self._cost_info_matrix[0][j] = cost_info_instance


		# Fill in the rest of the cost matrix
		for i in xrange(1, self._numRows):
			for j in xrange(1, self._numCols):
				
				# Create a Chooser object to register the row and column of the accumulated previous lowest cost (and not just the lowest cost)
				chooser = ci.Chooser()

				# We consider three previous positions - Pull them out of the matrix
				cost_info_1 = self._cost_info_matrix[i-1][j]
				cost_info_2 = self._cost_info_matrix[i][j-1]
				cost_info_3 = self._cost_info_matrix[i-1][j-1]

				# Add these three items to our chooser so we can find which one has the lowest accum cost
				chooser.add_cost_info_instance(cost_info_1)
				chooser.add_cost_info_instance(cost_info_2)
				chooser.add_cost_info_instance(cost_info_3)

				result = chooser.get_minimum_accum_cost_item()
				if result.success:
					best_prev_cost_item = result.item
					curr_local_cost = self._distance(self._Q[i], self._P[j])
					cost_info = ci.cost_info(i, j, local_cost=curr_local_cost)
					cost_info.add_info_from_prev_cost_info_instance(best_prev_cost_item.row, 
																	best_prev_cost_item.col, 
																	 best_prev_cost_item.local_cost,
																	 best_prev_cost_item.accum_cost)

					cost_info.accum_cost = cost_info.local_cost + cost_info.prev_accum_cost
					self._cost_info_matrix[i][j] = cost_info
					self._cost[i][j] = best_prev_cost_item.accum_cost + curr_local_cost 

				else:
					raise ValueError('Failure returned from Chooser: ' + result.message)

		# Return the Result object
		return utilsLib.Result(True,message='', item=None) 

	def get_global_cost(self):
		'''
		Returns the accumulated minimal-cost path for alignment.
		'''
		return self._cost[-1][-1]


	def print_cost_matrix(self):
		'''
		Prints the cost matrix
		'''
		if self._bverbose_mode and self._bprint_to_screen:
			print('\n\nThe _cost matrix: ',end="")	
			for row in self._cost:
				print('\n')
				for col in row:
					print(" %5.2f\t" % (col), end="")


	def print_cost_info_matrix(self):
		'''
		Prints the cost_info matrix
		'''
		if self._bverbose_mode and self._bprint_to_screen:
			print('\n\n_cost_info_matrix[][].accum_cost: ',end="")	
			for row in xrange(self._numRows):
				print('\n')
				for col in xrange(self._numCols):
					print('%5.2f\t' % (self._cost_info_matrix[row][col].accum_cost),end="")


			
	def print_backtrace_info(self, q_index, p_index, info_string):
		if self._bverbose_mode:
			logging.debug('Curr pos [Q-row: %d, P-col: %d] references cost_info: %s' % (q_index, p_index, info_string))


	def get_backtrace(self):
		'''
		Returns a list of cost_info objects starting from the end of the alignment and progress backwards towards the 
		start. This list of cost_info objects tells us the minimum-cost path and the row (Q) and column (P) indices tell 
		us which COriginPoint objects in the P sequence are associated (because of this alignment) with which COriginPoint 
		objects in the Q sequence.
		'''
		self._xBackTrace = []
		
		# Note: This is how the back-trace works:
		# The index of the current position is used to pull from the _cost_info_matrix a cost_info object which 
		# encodes the previous position. We use the coordinates of that previous position to pull out a the 
		# cost_info object that encodes the previous-previous position, and so on...
		#
		# The cost_info object stored in the matrix at the coordinates corrsponding to the current position
		# tell us where we came from.

		if self._bverbose_mode:
			logging.debug('\n')
			logging.debug('---------------- Start of get_backtrace() --------------------')
			logging.debug('\n')

		q_index = self._numRows-1
		p_index = self._numCols-1
		
		# Step 0. We assume we have a current_choice object (that was already appended to our list)
		current_position = self._cost_info_matrix[q_index][p_index]
		self._xBackTrace.append(current_position)
		self.print_backtrace_info(q_index, p_index, current_position.info_string)

		while True:

			# Step 1. Use the current_choice object to get previous indices
			prev_q_index = current_position.prev_row
			prev_p_index = current_position.prev_col

			# Step 2. If the previous indices are 0, then we know we're at the start and we're done
			if prev_q_index == 0 and prev_p_index == 0:
				#self.print_backtrace_info(prev_q_index, prev_p_index, current_position.info_string)
				self.print_backtrace_info(prev_q_index, prev_p_index, self._cost_info_matrix[0][0].info_string)
				return utilsLib.Result(True,message='', item=self._xBackTrace) 

			# Step 3. If the previous indices are NOT 0, then use the previous indices to pull the cost_info
			# object from matrix; call this current_position object, add it to our list and repeat
			else:
				current_position = self._cost_info_matrix[prev_q_index][prev_p_index]

			# Step 4. Add this Choice object to the end of our list
			self._xBackTrace.append(current_position)

			if self._bverbose_mode:
				self.print_backtrace_info(prev_q_index, prev_p_index, current_position.info_string)


	def process_backtrace(self):
		'''
		Prior to calling this method the client must first call compute_cost() to create the cost matrix and then it
		must next call get_backtrace() to create the _xBackTrace list from the cost matrix.
		This method iterates throught the _xBackTrace list to do the following for each ccost_info instance in this list:
		Note: An origin_point can have multiple estimate_points. But an estimate_point can only be assigned to one origin_point.
			- It gets the cost_info's column property, which it uses to get the estimate_point from the _P list
			- It gets the cost_info's row property, which it uses to get the origin_point from the _Q list
			- It sets the error and region parameters for the origin_point
			= It adds the estimate_point to the origin_point
			- It tells the estimate_point which origin_point it just got associated with. At the end if an estimate_point has
			  been associated with multiple origin_points, say, A, B and C, then we know we have to look at the local_cost for
			  each of these possible associations and only assign this estimate_point to the origin_point with the lowest local_cost.

		them to the appropriate origin_point instance as prescribed by the DTW alignment. It does this by calling the add_estimate_point()
		method
		'''
		if self._bverbose_mode:
			logging.debug('\n')
			logging.debug('---------------- Start of process_backtrace ----------------------')
			logging.debug('\n')

		# We iterate through the _xBackTrace list that we created in the get_BackTrace method to update the _Q and _P points.
		for cost_info_item in self._xBackTrace:

			row_in_backtrace = cost_info_item.row
			col_in_backtrace = cost_info_item.col
			local_cost = cost_info_item.local_cost


			# Get the cestimate_point instance corresponding to this column
			ep = self._P[col_in_backtrace]

			# Get the corigin_point instance corresponding to this row, set the rgion and error parameters
			# and then add the estimate_point to this origin_point (that it was associated with by the DTW alignment)
			op = self._Q[row_in_backtrace]
			op.add_estimate_point(ep)
			op.local_cost = local_cost

			# Now we tell this estimate_point about the origin_point it was assigned to. If we end up
			# assigning this estimate_point to multiple origin_points, then we will later have to go back 
			# and choose between them (and the origin_points not chosen run the risk of having a miss).
			ep.add_candidate_origin_point(op)

		# Manually fill in the 0th item:
		row_in_backtrace = 0
		col_in_backtrace = 0
		ep = self._P[col_in_backtrace]
		op = self._Q[row_in_backtrace]
		op.add_estimate_point(ep)
		
		# I don't know how to get the local cost since I don't have a real cost_info object for 0,0
		#op.local_cost = local_cost
		ep.add_candidate_origin_point(op)


		# Return the Result object
		return utilsLib.Result(True,message='', item=None)

	def post_process_origin_points(self):
		'''
		Prior to calling this method the client must first call compute_cost() to create the cost matrix. 
		Then it must call get_backtrace() to create the _xBackTrace list from the cost matrix.
		Then it must call process_backtrace() to add the estimate_points to their appropriate origin_points.
		
		'''

		if self._bverbose_mode:
			logging.debug('\n')
			logging.debug('---------------- Start of post_process_origin_points ----------------------')
			logging.debug('\n')

		# Get the dictionary of promiscuous estimate_points
		result = self._find_estimate_points_assigned_to_multiple_origin_points()
		if result.success:
			zest_pts_to_be_reconsidered = result.item 
			if self._bverbose_mode:
				logging.debug('\n\nPost-processing %d estimate_points which were assigned to multiple origin_points ...' % len(zest_pts_to_be_reconsidered))

			for name in zest_pts_to_be_reconsidered.keys():
				ep = zest_pts_to_be_reconsidered[name]
				

				chooser = origin_points.cpoint_chooser()

				# Get the list of this (promiscuous) ep's partners
				xorig_points = ep.get_candidate_origin_points()

				if self._bverbose_mode:
					logging.debug('estimate_point %s has %d candidate origin_points' % (ep.name, len(xorig_points)))

				# Add these partners (origin_points) to the chooser so we can decide which one is the winner
				for op in xorig_points:
					chooser.add_point(op)

				# Pick the winner partner (op)
				result = chooser.find_lowest_cost_origin_point()
				if result.success:
					result = chooser.get_lowest_cost_origin_point()
					if result.success:

						# Get the winner and tell the promiscuous ep which op it needs to settle down with
						op_winner = result.item
						ep.set_final_origin_point(op_winner)

						if self._bverbose_mode:
							logging.debug('Winning origin_point: %s' % op_winner.name)

						# Get the loser origin_points and then tell each of them to remove 
						# this promiscuous ep from its little black book - This ep has settled down
						# with another (lowest-cost) op.
						result = chooser.get_loser_origin_points()
						if result.success:
							xop_losers = result.item
							for op in xop_losers:
								result=op.remove_estimate_point(ep)
								if result.success:
									if self._bverbose_mode:
										logging.debug('estimate_point: %s removed from origin_point: %s' % (ep.name, op.name))
								else:
									if self._bverbose_mode:
										logging.debug('Failed to remove estimate_point: %s from origin_point: %s' % (ep.name, op.name))

		# Return the Result object
		return utilsLib.Result(True,message='', item=None)

	def _find_estimate_points_assigned_to_multiple_origin_points(self):
		'''
		In the process_backtrace method, an estimate_point could be associated by the DTW alignment to multiple 
		origin_points. When we calculate costs at each orgin_point, we can't have estimate_points associated 
		with multiple origin_points.

		This private method returns (through a Result object) a dictionary of estimate_points that each have 
		multiple (candidate) origin_points. The estimate_points in this dictionary need to be processed to 
		idenitfy among the candidates the lowest-cost origin point and associate the estimate_point with only 
		that origin_point.
		'''
		zest_pts_to_be_reconsidered = {}

		# Iterate through all of our origin_points
		for op in self._Q:

			# Get the estimate_points associated with this origin_point
			zestimate_points = op.get_estimate_points()

			# Iterate through the estimate_points assigned to this origin_point
			for key in zestimate_points.keys():
				ep = zestimate_points[key]
			
				# Identify the estimate_points that have multiple candidate origin_points
				if ep.num_candidate_origin_points > 1:

					# Build a dictionary of estimate_points that have multiple candidate origin_points
					zest_pts_to_be_reconsidered[ep.name] = ep

		return utilsLib.Result(True,message='', item=zest_pts_to_be_reconsidered)


			
if __name__ == "__main__":


	# This is the same set we used for T2:
	# seqQ = [ pt.CPoint(0, 1), pt.CPoint(1, 3), pt.CPoint(1, 6), pt.CPoint(3, 9),					pt.CPoint(1, 12), pt.CPoint(1, 15) ]
	# seqP = [				  pt.CPoint(2, 3), pt.CPoint(3, 6), pt.CPoint(2, 9), pt.CPoint(4, 10),	pt.CPoint(2, 12) ]

	# Ground truth MDAT file
	Q_originPoints_GT = oplist.COriginPointsList()
	result = Q_originPoints_GT.read_mdat(r'C:\tmp10\img1_gt.mdat')
	if result.success:
		result = Q_originPoints_GT.get_info_list()
		if result.success:
			print('The ground truth origin points: ')
			for sInfo in result.item:
				print(sInfo)
		else:
			print('Error calling getInfoList() method: ' + result.message)
	else:
		print('Error reading and parsing ground-truth MDAT file: ' + result.message)

	# Estimates MDAT file
	P_originPoints_Est = oplist.COriginPointsList()
	result = P_originPoints_Est.read_mdat(r'C:\tmp10\img1_est.mdat')
	if result.success:
		result = P_originPoints_Est.get_info_list()
		if result.success:
			print('The estimate origin points: ')
			for sInfo in result.item:
				print(sInfo)
		else:
			print('Error calling getInfoList() method: ' + result.message)
	else:
		print('Error reading and parsing estimate MDAT file: ' + result.message)


	try:
		aligner = dtw_aligner(Q_originPoints_GT, P_originPoints_Est, True)
	except:
		print('Exception thrown in dtw_aligner constructor. Details: ' + utilsLib.getExceptionDetails())
		exit()
		

	# Look at distances to see what went wrong
	for iRow in xrange(0, len(aligner._Q)):
		print('\nRow: ' + str(iRow))
		for iCol in xrange(0, len(aligner._P)):
			p1 = aligner._Q[iRow]
			p2 = aligner._P[iCol]
			d = aligner._distance(p1, p2)
			print('Distance between (%d, %d) and (%d, %d): %f' % (p1.x, p1.y, p2.x, p2.y, d))



	try:
		result = aligner.create_empty_cost_matrix()
		if not result.success:
			print('Error returned from aligner.create_empty_cost_matrix(). Details: ' + result.message)
	except:
		print('Exception thrown in dtw_aligner.create_empty_cost_matrix method. Details: ' + utilsLib.getExceptionDetails())
		exit()

	try:
		#result = aligner.create_empty_choices_matrix()
		result = aligner.create_empty_cost_info_matrix()
		if not result.success:
			print('Error returned from aligner.create_empty_choices_matrix(). Details: ' + result.message)
	except:
		print('Exception thrown in dtw_aligner.create_empty_choices_matrix method. Details: ' + utilsLib.getExceptionDetails())
		exit()

	# Compute the cost matrix
	result = aligner.compute_cost()
	if result.success:
		fCost = aligner.get_global_cost()
		print ("\n\nGlobal Cost: " + str(fCost))

		aligner.print_cost_matrix()

		# Compute the minimum-cost path back through the cost matrix
		result = aligner.get_backtrace()
		if result.success:
			# We get the backtrace, but we ignore it if everthing is working
			xBackTrace = result.item

			# Iterate through the backTrace list
			for cost_info_item in xBackTrace:
				print(cost_info_item.info_string)

			# Process the backtrace to associate estimate_points with origin_points
			result = aligner.process_backtrace()
			if result.success:
				result = aligner.post_process_origin_points()
				if result.success:
					zestimate_points_to_be_fixed = result.item

					# print out the estimate_points that need fixing
					for k in zestimate_points.keys:
						est_point = zestimate_points[k]
						print('estimate_point: ' + est_point.name + ' ' + est_point.info_string)

	print('Made it this far ... ')
	

	#xOriginPoints = aligner.get_OriginPoints()
	#for op1 in xOriginPoints:
	#	print(op1.info_string)

	print ("Done ...")