# origin_point.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import os
import sys
from types import *

import logging
import point as pt
import estimate_point as ep
import utilsLib
import region_parameters as rp
import region
import origin_point_costs as opc

class corigin_point(pt.cpoint):
	'''
	corigin_point is a class derived from the cpoint class. An instance of corigin_point is used to hold
	the data for a ground-truth origin point.
	'''


	def __init__(self, x, y, name='', index=-1):
		'''
		Client code must supply the (x, y) coordinate, which is the column and row of origin point 
		for the text-line segment. The client can optionally supply a name or ID for this point and 
		its ordering relative to other instances in its parent container.
		'''
		assert type(x)			is IntType, "x is not an integer: %s" % str(x)
		assert type(y)			is IntType, "y is not an integer: %s" % str(y)
		assert type(name)		is StringType, "name is not a string: %s" % name
		assert type(index)		is IntType, "index is not an integer: %s" % str(index)
		
		# Invoke the base class constructor
		pt.cpoint.__init__(self, x, y, 'Q'+ name, index)


		# Fields:
		self._bverbose_mode = False
		self._local_cost = -1.0
		self._zestimate_points = {}

		self._origin_point_costs = None
		self._region_parameters = None
		self._error_parameters = None
		self._region = None
		self._top_neighbor_y = None
		self._top_neighbor_vertical_distance = None
		self._bottom_neighbor_y = None
		self._bottom_neighbor_vertical_distance = None

		logging.debug('corigin_point constructor: ' + self.info_string)


	@property
	def verbose_mode(self):
		return self._bverbose_mode

	@verbose_mode.setter
	def verbose_mode(self, value):
		self._bverbose_mode = value

	@property
	def local_cost(self):
		return self._local_cost

	@local_cost.setter
	def local_cost(self, cost):
		self._local_cost = cost

	@property
	def alignment_string(self):
		return self.name + ' Local cost: ' + self.local_cost + ' Num estimate_points: ' + len(self._zestimate_points)

	def set_top_neighbor_y(self, top_neighbor_y):
		if top_neighbor_y:
			self._top_neighbor_y = top_neighbor_y
			self._top_neighbor_vertical_distance = self.y - top_neighbor_y

	def set_bottom_neighbor_y(self, bottom_neighbor_y):
		if bottom_neighbor_y:
			self._bottom_neighbor_y = bottom_neighbor_y
			self._bottom_neighbor_vertical_distance = bottom_neighbor_y - self.y

	def set_error_parameters(self, error_params):
		self._error_parameters = error_params

	def set_region_parameters(self, reg_parameters):
		self._region_parameters = reg_parameters

	def create_tolerance_region(self):
		'''
		This method creates the cregion instance for this origin_point. 
		'''
		try:
			self._region = region.cregion(self._region_parameters, 
										  self._top_neighbor_vertical_distance,
										  self._bottom_neighbor_vertical_distance)
		except:
			smsg = 'Exception thrown calling the cregion constructor. Details. ' + utilsLib.getExceptionDetails()
			return utilsLib.Result(False, message=smsg, item=None)

		# create a cpoint instance and use it to call the set_center_point method
		center_point = pt.cpoint(self.x, self.y, self.name, self.index)
		self._region.set_center_point(center_point)
		return utilsLib.Result(True, '', None)


	def calculate_costs(self):
		'''
		Calculates the costs associated with this origin_point, which are saved in the origin_point_costs instance.
		'''
		if self._bverbose_mode:
			logging.debug('+++++++Calculating costs for origin_point %s at (%d, %d) with %d estimate_points.' % (self.name, self.x, self.y, len(self._zestimate_points.keys())))

		# Create the object that will hold the values for the various costs
		self._origin_point_costs = opc.corigin_point_costs(self._error_parameters)

		# Create list of estimate_points from our dictionary
		xestimate_points = []
		for key in self._zestimate_points.keys():
			ep = self._zestimate_points[key]
			xestimate_points.append(ep)

		# 1. Is there an estimate_point for this origin_point? Save away the number
		num_estimate_points = len(xestimate_points)
		self._origin_point_costs.num_estimate_points = num_estimate_points
		if self._bverbose_mode:
			logging.debug('Number of estimate_points for this origin_point: %d' % (num_estimate_points))

		#2. If there are no estimate_points, register this as a detection failure
		if num_estimate_points == 0:
			# cost_for_miss = self._error_parameters.cost_for_miss
			self._origin_point_costs.register_detection_failure()
			if self._bverbose_mode:
				logging.debug('Registered a detection failure.')
			return utilsLib.Result(True, message='', item = None)

	
		# 3. If there is a single estimate_point, register its type
		if num_estimate_points == 1:
			self._origin_point_costs.num_estimate_points = num_estimate_points
			ep = xestimate_points[0]
			if self._bverbose_mode:
				logging.debug('One estimate_point: %s, (%d, %d)' % (ep.name, ep.x, ep.y))

			if self._region.is_this_ep_an_r1_hit(ep):
				self._origin_point_costs.register_r1_hit()
				logging.debug('\t\tThis single ep is an r1 hit')
			elif self._region.is_this_ep_an_r2_hit(ep):
				distance = self._region.distance_from_center_point(ep)
				self._origin_point_costs.register_r2_hit(distance)
				logging.debug('\t\tThis single ep is an r2 hit')
			else:
				distance = self._region.distance_from_center_point(ep)
				self._origin_point_costs.register_proximity_miss(distance)
				logging.debug('\t\tThis single ep is a miss')

		# 4. There are multiple estimate_points, register their types
		else:
			self._origin_point_costs.num_estimate_points = num_estimate_points
			if self._bverbose_mode:
				logging.debug('\t\tMultiple estimate_points ...')
		
			# Ask the cregion instance to return the estimate_points that are hits
			xr1_items = self._region.get_r1_hits_and_distances(xestimate_points)
			for item in xr1_items:
				ep = item[0]
				distance = item[1]
				
				# We're going to ignore distances if the ep is inside r1
				self._origin_point_costs.register_r1_hit()

			if self._bverbose_mode:
				logging.debug('\t\tNumber of r1 hits: ' + str(len(xr1_items)))

			xr2_items = self._region.get_r2_hits_and_distances(xestimate_points)
			for item in xr2_items:
				ep = item[0]
				distance = item[1]
				self._origin_point_costs.register_r2_hit(distance)

			if self._bverbose_mode:
				logging.debug('\t\tNumber of r2 hits: ' + str(len(xr2_items)))

			xr3_items = self._region.get_r3_hits(xestimate_points)
			for ep in xr3_items:
				self._origin_point_costs.register_r3_hit()

			if self._bverbose_mode:
				logging.debug('\t\tNumber of misses: ' + str(len(xr3_items)))

		return utilsLib.Result(True,'', None)


	def get_costs(self):
		'''
		This method returns (through a Result instance) the cost resulting from the associations of the 
		estimate_point(s) with this origin_point. This method must be called only after calculate_costs 
		has been called.
		'''
		
		# Validate that the hits and misses were registered correctly
		result = self._origin_point_costs.validate_registered_values()
		if not result.success:
			smsg = 'Error returned fromn origin_point_costs.validate_registered_values. Details: ' + result.message
			return utilsLib.Result(False, message=smsg, item=None)

		result = self._origin_point_costs.get_cost()
		if result.success:
			if self._bverbose_mode:
				logging.debug('Total costs calculated in get_costs for origin_point %s: %5.2f' % (self.name, result.item))
			return utilsLib.Result(True, '', item = result.item)
		else:
			smsg = 'Error returned in get_costs from the call to _origin_point_costs.get_cost(). Details: ' + result.message
			return utilsLib.Result(False, smsg, item=None)


	def add_estimate_point(self, estimate_point):
		'''
		This origin_point can have multiple estimate_points assigned to it. The closest one
		is the one we use to compute the region cost and the rest are considered (and scored
		as) false alarms.
		'''
		self._zestimate_points[estimate_point.name] = estimate_point

	def remove_estimate_point(self, estimate_point):
		'''
		Removes the specified estimate_point from the dictionary of points associated with this origin_point.
		'''
		key = estimate_point.name
		try:
			if self._zestimate_points.has_key(key):
				del self._zestimate_points[key]
		except:
			smsg = 'Exception thrown trying to remove the estimate_point with the following name: ' + estimate_point.name + ' Details: ' + utilsLib.getExceptionDetails()
			return utilsLib.Result(False,message=smsg, item=None)

		return utilsLib.Result(True,message='', item=None)

	def get_estimate_points(self):
		'''
		'''
		return self._zestimate_points

	def get_estimate_points_string(self):
		'''
		Returns a string representation of the estimate_points associated with this origin_point.
		'''
		ep_string = 'origin_point ' + self.name + ': '
		for key in self._zestimate_points.keys():
			ep = self._zestimate_points[key]
			ep_string += ' ' + ep.name + ' '
		return ep_string


if __name__ == "__main__":

	pt1 = corigin_point(13, 42, "ID_1")
	print(pt1.info_string)

	pt2 = corigin_point(13, 42, "ID_2", index=0)
	print(pt2.info_string)

	pt3 = corigin_point(13, 42, name="ID_3", index=0)
	print (pt3.info_string)

	pt4 = corigin_point(13, 42, index=0)
	pt4.name = "ID_4"
	print (pt4.info_string)

	pt5 = corigin_point(0, 1, "ID_5")
	pt5.index = 5
	print (pt5.info_string)

	try:
		pt1_bogus = corigin_point(1.2, 3, "Bogus")
	except AssertionError:
		print('Exception thrown calling the corigin_point constructor: ' + utilsLib.getExceptionDetails())

	# Stuff related to the origin_point's estimate_points
	ep1 = ep.cestimate_point(24, 60, name = "24601", index = 0)
	ep2 = ep.cestimate_point(31, 45, name = "31459", index = 1)

	pt1.add_estimate_point(ep1)
	pt1.add_estimate_point(ep2)

	
	# Stuff related to this origin_point's region
	region_params = rp.cregion_parameters(r1_top_height_percent=0.50,
										r1_bottom_height_percent=0.50,
										r1_width_multiplier=2.0,
										r2_top_height_percent=1.0,
										r2_bottom_height_percent=1.0,
										r2_width_multiplier=3.0)

	pt1.set_region_parameters(region_params)
	pt1.create_region(top_height = 100, bottom_height = 200)
		

	

	
	print('Done ...')