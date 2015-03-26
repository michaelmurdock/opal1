# cost_info.py
# 
from __future__ import print_function

import sys
import utilsLib

class cost_info(object):
	'''
	cost_info is a elper classes for making it easier to backtrace through the DTW 
	alignment cost matrix.

	In the DTW cost matrix calculation at each particular position, when you are
	in the _current_ position, three previous positions must be checked to see which 
	one represents the lowest accumulated cost to that point. An instance of the 
	cost_info class is used to model what is known about the cost in the current 
	position, the local and accumulated costs in the previous position and the 
	location (row, col) of that previous position. 
	'''
	def __init__(self, row, col, local_cost = 0.0, accum_cost=0.0, prev_accum_cost = 0.0):
		'''
		The constructor requires the client call it with the location (row and column 
		indexes) of the current position. The client can optionally supply three kinds
		of costs: current local and accumulated costs and the accumulated cost for the
		previous position. 
	   
	    The two costs for the current position are the following:
			_local_cost - The distance between the two points specified by the row and col indices.
			_accum_cost - The sum of the accum cost from the previous position and the _local_cost.
	
		The two costs for the previous postion are the following:
			_prev_local_cost - the distance between the two points specified by the _prev_row and _prev_col coordinates.
			_prev_accum_cost - the accumulated cost from the previous position (see _accum_cost for exact definition).

		'''
		# Data for the current position
		self._row = row
		self._col = col
		self._accum_cost = accum_cost
		self._local_cost = local_cost

		# Data for the previous position
		self._prev_row = 0
		self._prev_col = 0
		self._prev_accum_cost = prev_accum_cost
		self._prev_local_cost = 0 


		
	
	def add_info_from_prev_cost_info_instance(self, row, col, local_cost, accum_cost):
		'''
		Called with the information about the position that is previous to the current position
		'''
		self._prev_row = row
		self._prev_col = col
		self._prev_local_cost = local_cost
		self._prev_accum_cost = accum_cost


	@property
	def row(self):
		return self._row

	@property
	def col(self):
		return self._col
	
	@property
	def local_cost(self):
		return self._local_cost

	@local_cost.setter
	def local_cost(self, cost):
		self._local_cost = cost

	@property
	def accum_cost(self):
		return self._accum_cost
	
	@accum_cost.setter
	def accum_cost(self, accum_cost):
		self._accum_cost = accum_cost

	@property
	def prev_row(self):
		return self._prev_row

	@property
	def prev_col(self):
		return self._prev_col

	@property
	def prev_accum_cost(self):
		return self._prev_accum_cost

	@prev_accum_cost.setter
	def prev_accum_cost(self, prev_accum_cost):
		self._prev_accum_cost = prev_accum_cost

	@property
	def prev_local_cost(self):
		return self._prev_local_cost

	@property
	def info_string(self):
		#return 'Row: ' + str(self.row) + ', Col: ' + str(self.col) + ', Prev Accum Cost: ' + str(self.prev_accum_cost) + ', Local Cost: ' + str(self.local_cost) + ', Accum Cost: ' + str(self.accum_cost)
		s = 'Row: %5.2f, Col: %5.2f, Local Cost: %5.2f, Accum Cost: %5.2f, Prev Row: %d, Prev Col: %d, Prev Accum Cost: %5.2f' % (self.row, self.col, self.local_cost, self.accum_cost, self.prev_row, self.prev_col, self.prev_accum_cost)
		return s

class Chooser(object):
	'''
	An instance of the Chooser class is used in the DTW cost calculation as a way to keep track of 
	the row and column associated with each cost calculation. 
	
	This is how the Chooser class is intended to be used:
	
	1. The client must create cost_info objects, 
	2. Client adds cost_info objects with calls to the add_cost_info method.
	3. Client calls the get_minimum_accum_cost_item to find which of the added cost_info
	instnaces has the lowest accum_cost value.
	'''
	def __init__(self):
		'''
		Constructor for the Chooser class.
		An instance of this class is used to compare the costs of cost_info instances.
		'''
		self._xcost_info_instances = []
		
	def add_cost_info_instance(self, cost_info_instance):
		'''
		This method is used to add cost_info instances for subsequent comparison to find the minimum-
		cost instance with the get_minimum_accum_cost_item method.

		This method does not return a value.
		'''
		self._xcost_info_instances.append(cost_info_instance)
		

	def get_minimum_accum_cost_item(self):
		'''
		Iterate through the cost_item instances and return the one with the lowest accum_cost value.
		The return value is a Result object with a reference to the lowest-cost cost_info object.

		Prior to calling this method the client must have previously called the add_cost_info_instance
		method to add cost_info objects.

		Although any number of techniques could be used for selecting between the added choices, this
		method is the basic way to iterate through the added cost_info objects and return the one corresponding 
		to the lowest cost (the cost_info object with the lowest accum_cost)
		'''
		if len(self._xcost_info_instances) == 0:
			sMsg1 = 'No cost_info instances were found.'
			sMsg2 = ' Call add_cost_info_instance() with at least two cost_info instances and then call this method to choose between them.'
			return utilsLib.Result(False, sMsg1 + sMsg2)

		# This is our initial (fake best) choice
		best_cost_info = cost_info(0,0, accum_cost=sys.maxint)
		bKept_initial_fake_item = True
		
		for item in self._xcost_info_instances:
			if item.accum_cost < best_cost_info.accum_cost:
				best_cost_info = item
				bKept_initial_fake_item = False

		if bKept_initial_fake_item:
			return utilsLib.Result(False,'Never found a cost_info item with lower cost than the initial fake one!')
		else:
			return utilsLib.Result(True,'', best_cost_info)

if __name__ == "__main__":

	# ------------- Test #1

	chooser1 = Chooser()
	result = chooser1.get_minimum_accum_cost_item()
	if not result.success:
		print('Error: ' + result.message)


	# ------------ Test #2

	c1 = cost_info(1,2, prev_accum_cost=12.0)
	c1.local_cost = 3.0
	c1.accum_cost = 13.0
	print(c1.info_string)

	c2 = cost_info(2,3, accum_cost=23.0)
	c2.local_cost = 1.5
	c2.prev_accum_cost = 3.0
	print(c2.info_string)



	c3 = cost_info(4,5, local_cost=4.5)

	
	
	print(c1.accum_cost)

	
	print(c1.accum_cost)
	

	# ------------ Test #3

	chooser = Chooser()
	chooser.add_cost_info_instance(c1)
	chooser.add_cost_info_instance(c2)
	chooser.add_cost_info_instance(c3)
	

	result = chooser.get_minimum_prev_cost_choice()
	if result.success:
		minimum_cost_item = result.item
		print(minimum_cost_item.info_string)

	print('Done ... ')
