# origin_point_costs.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import utilsLib

class corigin_point_costs(object):
	'''
	An instance of this class holds the different kinds of costs that are calculated for a particular origin_point.

	Naming convention:
		Detection Failure: If the DTW alignment did not assiciate an estimate_point with an origin_point
		Proximity Miss: An estimate_point that is outside R2
		R1-Hit: An estimate_point that is inside R1
		R2-Hit: An estimate_point that is inside R2 (but outisde R1)
	'''
	def __init__(self, error_params):
		'''
		'''
		self._error_params = error_params

		# Set to True by a call to register_detection_failure(). 
		# This property can also have its boolean value set by detection_miss(value)
		self._bdetection_failure = False

		# Set with the num_estimate_points property setter
		# Accessed through the num_estimate_points property getter
		self._num_estimate_points = 0

		# Incremented by 1 with every call to register_r1_hit property setter.
		# Accessed through the num_r1_hits property
		self._num_r1_hits = 0

		# Values are added to this list by calling register_r2_hit().
		# The length of this list is used to compute the value returned from the num_r2_hits property.
		# get_cost uses the zero'th value as the value passed into the _calculate_r2_cost method.
		self._xr2_hit_distances = []

		# Values are added to this list by calling register_proximity_miss()
		# This value is retrieved by calling the property num_proximity_misses
		self._xmiss_distances = []

		# I think this is the same as a proximit miss, but separated out to make it easier to
		# identify during debugging where the "miss" came from
		self._num_r3_hits = 0

	@property
	def num_estimate_points(self):
		return self._num_estimate_points

	@num_estimate_points.setter
	def num_estimate_points(self, count):
		self._num_estimate_points = count

	@property
	def num_r1_hits(self):
		return self._num_r1_hits

	@property
	def num_r2_hits(self):
		return len(self._xr2_hit_distances)

	@property
	def num_proximity_misses(self):
		return len(self._xmiss_distances)
	
	@property
	def num_r3_hits(self):
		return self._num_r3_hits
		
	def register_detection_failure(self):
		self._bdetection_failure = True

	def register_r1_hit(self):
		self._num_r1_hits += 1

	def register_r2_hit(self, distance):
		self._xr2_hit_distances.append(distance)

	def register_r3_hit(self):
		self._num_r3_hits += 1

	def register_proximity_miss(self, distance):
		self._num_r3_hits += 1

	@property
	def detection_miss(self):
		return self._bdetection_failure

	@detection_miss.setter
	def detection_miss(self, value):
		self._bdetection_failure = value

	def validate_registered_values(self):
		'''
		origin_point.get_costs calls this method to validate the total number of hits and misses found in 
		the origin_point.calculate_costs method exactly equals the number of estimate_points. Anything else
		is the result of a bug.
		'''
		if self.num_estimate_points == 0 and not self.detection_miss:
			smsg = 'Error: Number of estimate_points is 0, but the detection_miss flag is False!'
			return utilsLib.Result(False, message=smsg, item=None)
		num_registered_values = 0
		num_registered_values += self.num_r1_hits + self.num_r2_hits + self.num_proximity_misses + self.num_r3_hits
		if num_registered_values != self.num_estimate_points:
			smsg = 'Error: Number of estimate_points: %d, Number of registered values: %d' % (self.num_estimate_points, num_registered_values)
			return utilsLib.Result(False, message=smsg, item=None)
		return utilsLib.Result(True,'', item=None)

	def _calculate_r2_cost(self, distance):
		'''
		Private method that returns the cost for an estimate_point in region2, which is proportional to the passed-in distance.
		'''
		if distance < 0.001:
			logging.debug('A very small distance was passed into _calculate_r2_cost(). Clamping it to small value to avoid divide-by-zero exception')
			distance = 0.001
		penalty = self._error_params.cost_for_miss
		scaled_distance = (distance - 1.0) / distance
		r2_cost = penalty * scaled_distance
		return r2_cost


	def get_cost(self):
		'''
		Tabulates and returns the total cost due to the hits and misses found from the previous call to origin_point.calculate_costs().
		'''
		# Detection Failure
		if self.num_estimate_points == 0:
			cost = self._error_params.cost_for_miss
			return utilsLib.Result(True,'', item=cost)

		# Single estimate's cost depends on if it is in r1, r2, or outside r2
		if self.num_estimate_points == 1:

			# r1 hit
			if self.num_r1_hits == 1:
				cost = 0.0
				return utilsLib.Result(True,'',item=cost)

			# r2 hit
			if self.num_r2_hits == 1:
				distance = self._xr2_hit_distances[0]
				cost = self._calculate_r2_cost(distance)
				return utilsLib.Result(True,'', item=cost)

			# outside r2 ==> miss
			if self.num_proximity_misses == 1:
				cost = self._error_params._cost_for_miss
				return utilsLib.Result(True, '', item=cost)

			# This is where I am tabulating r3 hits (which is the same as a proximity miss
			if self._num_r3_hits == 1:
				cost = self._error_params._cost_for_miss
				return utilsLib.Result(True, '', item=cost)

			else:
				return utilsLib.Result(False, 'Number of estimate_points is 1, but cost is unknown!', item=None)

		# Multiple estimates means we have false positive costs
		if self.num_estimate_points > 1:

			# Start by assuming that only 1 point can be a hit, the rest are false positives
			# Note: with multiple estimate_points, there is no miss
			num_false_positives = self.num_estimate_points - 1
			false_positive_cost = num_false_positives * self._error_params.cost_per_false_alarm
			
			# If we have at least one R1-Hit, then its cost is zero and all the rest are false positives
			if self.num_r1_hits >= 1:
				cost = false_positive_cost
				return utilsLib.Result(True, '', item=cost)

			# If we have at least one R2-Hit, then its cost depends on the distance and all the rest are false positives
			if self.num_r2_hits >= 1:
				distance = self._xr2_hit_distances[0]
				cost = self._calculate_r2_cost(distance)
				cost += false_positive_cost
				return utilsLib.Result(True, '', item=cost)

			# If we're here then it means we have multiple estimate_points, we have 0 r1 hits and 0 r2 hits
			# We have all misses, which means they are all penalized as false positives
			cost = self.num_estimate_points * self._error_params.cost_per_false_alarm
			return utilsLib.Result(True, '', item=cost)




