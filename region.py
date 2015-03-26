# region.py
#
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import math

import point as pt
import utilsLib
import region_parameters as rp


class cregion(object):
	'''
	A cregion instance (called a region) is the tolerance region around an origin_point, 
	which is the center point of region. A region actually consists of two regions, R1 and R2, 
	which are used to calculate a cost score for estimate_points that attempt to be as close as
	possible to the origin_point (the center point).

	A region needs region_parameters, 


	Public Methods:
		set_center_point(center_point)
		distance_from_center_point(ep)
		is_this_ep_an_r1_hit(ep)
		is_this_ep_an_r2_hit(ep)
		get_r1_hits_and_distances(xestimate_points)

	'''
	def __init__(self, region_parameters, top_height=None, bottom_height=None):
		'''
		Lorem, Ipsum, ...
		'''
		if top_height == None and bottom_height == None:
			raise ValueError('cregion constructor requires at least one non-null height!')

		self._cost = -1.0

		# top_height == None means this is the top line; use the bottom_height for the top_height value
		# bottom_height == None means this is the bottom line; use the top_height for the bottom height value
		if top_height == None:
			top_height = bottom_height

		if bottom_height == None:
			bottom_height = top_height

		self._rparams = region_parameters
		self._top_height = top_height
		self._bottom_height = bottom_height


		# r1 constants
		self._r1_top_height  = self._rparams.r1_top_height_percent * top_height
		self._r1_bottom_height = self._rparams.r1_bottom_height_percent * bottom_height
		
		min_r1_height = min(self._r1_top_height, self._r1_bottom_height)

		#self._r1_right_width = self._r1_top_height * self._rparams.r1_width_multiplier
		#self._r1_left_width  = self._r1_top_height * self._rparams.r1_width_multiplier
		self._r1_right_width = min_r1_height * self._rparams.r1_width_multiplier
		self._r1_left_width  = min_r1_height * self._rparams.r1_width_multiplier


		# r2 constants
		self._r2_top_height    = self._rparams.r2_top_height_percent * top_height
		self._r2_bottom_height = self._rparams.r2_bottom_height_percent * bottom_height
		
		min_r2_height = min(self._r2_top_height, self._r2_bottom_height)

		#self._r2_right_width   = self._r2_top_height * self._rparams.r2_width_multiplier
		#self._r2_left_width    = self._r2_top_height * self._rparams.r2_width_multiplier
		self._r2_right_width   = min_r2_height * self._rparams.r2_width_multiplier
		self._r2_left_width    = min_r2_height * self._rparams.r2_width_multiplier

	def set_center_point(self, center_point):
		'''
		This method is called after the constructor with a particular cpoint instance.
		Note that after the constructor is called, client code can call this method mulitple times to
		create new regions. In other words, you only call the constructor once, but you can define
		multiple regions with calls to this method.
		'''
		self._cp = center_point

		# Derived values - region r1
		self._r1_x_lhs = center_point.x - self._r1_left_width
		self._r1_x_rhs = center_point.x + self._r1_right_width
		self._r1_y_top = center_point.y - self._r1_top_height
		self._r1_y_bottom = center_point.y + self._r1_bottom_height

		# Derived values - region r2
		self._r2_x_lhs    = center_point.x - self._r2_left_width
		self._r2_x_rhs    = center_point.x + self._r2_right_width
		self._r2_y_top    = center_point.y - self._r2_top_height
		self._r2_y_bottom = center_point.y + self._r2_bottom_height

		# Derived values - region r3
		# self._xr3_estimate_points = []

	
	def distance_from_center_point(self, ep):
		'''
		Returns the Euclidean distance of the specified estimate_point to the center_point, self._cp.
		'''
		return math.sqrt(math.pow((self._cp.x - ep.x), 2.0) + math.pow((self._cp.y - ep.y), 2.0))
	
		
	def is_this_ep_an_r1_hit(self, ep):
		'''
		This method returns True if the specified estimate_point is within r1, False otherwise
		'''
		est_pt = pt.cpoint(ep.x, ep.y, ep.name, ep.index)
		bhit = False
		if est_pt.x < self._r1_x_rhs and est_pt.x > self._r1_x_lhs and est_pt.y > self._r1_y_top and est_pt.y < self._r1_y_bottom:
			bhit = True
		return bhit


	def is_this_ep_an_r2_hit(self, ep):
		'''
		This method returns True if the specified estimate_point is within r2, False otherwise
		'''
		est_pt = pt.cpoint(ep.x, ep.y, ep.name, ep.index)
		bhit = False

		left_of_r1 = False
		right_of_r1 = False
		above_r1 = False
		below_r1 = False

		# Left of R1
		if est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r1_x_lhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r2_y_bottom:
			left_of_r1 = True
		# Right of R1
		if est_pt.x >= self._r1_x_rhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r2_y_bottom:
			right_of_r1 = True
		# Above R1
		if est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r1_y_top:
			above_r1 = True
		# Below R1
		if est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r1_y_bottom and est_pt.y <= self._r2_y_bottom:
			below_r1 = True

		if left_of_r1 or right_of_r1 or above_r1 or below_r1:
			bhit = True

		#if ((est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r1_x_rhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r2_y_bottom) or \
		#	# Right of R1
		#	(est_pt.x >= self._r1_x_rhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r2_y_bottom) or \
		#	# Above R1
		#	(est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r2_y_top and est_pt.y <= self._r1_y_top) or \
		#	# Below R1
		#	(est_pt.x >= self.b_r2_x_lhs and est_pt.x <= self._r2_x_rhs and est_pt.y >= self._r1_y_bottom and est_pt.y <= self._r2_y_bottom)):
		#	   hit = True
		return bhit

	def is_this_ep_an_r3_hit(self, ep):
		'''
		This method returns True if the specified estimate_point is outside r2, False otherwise
		'''
		est_pt = pt.cpoint(ep.x, ep.y, ep.name, ep.index)
		bhit = False
		if  est_pt.x > self._r2_x_rhs or \
			est_pt.x < self._r2_x_lhs or \
			est_pt.y < self._r2_y_top or \
			est_pt.y > self._r2_y_bottom:
			bhit = True
		return bhit

	def get_r1_hits_and_distances(self, xestimate_points):
		'''
		This method iterates through the passed-in list of estimate_points to find if any of them
		are within r1. For each estimate_point that is within r1, a two-item list is created of the 
		following form: [ep, distance]. If this method finds multiple hits, the returned list will 
		contain multiple two-item lists.
		'''
		xr1_hits =[]
		for ep in xestimate_points:
			if self.is_this_ep_an_r1_hit(ep):
				d = self.distance_from_center_point(ep)
				xr1_hits.append([ep, d])
		return xr1_hits

	def get_r2_hits_and_distances(self, xestimate_points):
		'''
		This method iterates through the passed-in list of estimate_points to find if any of them
		are within r2. For each estimate_point that is within r2, a two-item list is created of the 
		following form: [ep, distance]. If this method finds multiple hits, the returned list will 
		contain multiple two-item lists.
		'''
		xr2_hits =[]
		for ep in xestimate_points:
			if self.is_this_ep_an_r2_hit(ep):
				d = self.distance_from_center_point(ep)
				xr2_hits.append([ep, d])
		return xr2_hits

	def get_r3_hits(self, xestimate_points):
		'''
		This method iterates through the passed-in list of estimate_points to find if any of them
		are outside of r2, which is r3. Each estimate_point that is outside r2 is added to a list
		that is returned.
		'''
		xr3_hits =[]
		for ep in xestimate_points:
			if self.is_this_ep_an_r3_hit(ep):
				xr3_hits.append(ep)
		return xr3_hits

	#def compute_cost(self, pt):
	#	'''
	#	'''
	#	# First, we check if this pt is inside R2
	#	if pt.x < r2_x_rhs and pt.x > r2_x_lhs and pt.y > r2_y_top and pt.y < r2_y_bottom:

			
	#		if pt.x < r1_x_rhs and pt.x > r1_x_lhs and pt.y > r1_y_top and pt.y < r1_y_bottom:
	#			# We're inside R1:
	#			self._cost = 0.0

	#		else:
	#			# We're inside R2:
	#			distance_squared = pow((pt.x - self._cp.x), 2) + pow((pt.y - self._cp.y), 2)
	#			self._cost = math.sqrt(distance_squared)
	#			return self._cost



	@property
	def info_string(self):
		return 'Top left corner: (%d, %d), Top right corner: (%d, %d), Bottom left corner: (%d, %d), Bottom right corner: (%d, %d)' % (self._r1_x_lhs, self._r1_y_top,
																																 self._r1_x_rhs, self._r1_y_top, self._r1_x_lhs, 
																																 self._r1_y_bottom,self._r1_x_rhs, self._r1_y_bottom)




if __name__ == "__main__":

	reg_params1 = rp.cregion_parameters(r1_top_height_percent=0.50,
										r1_bottom_height_percent=0.50,
										r1_width_multiplier=2.0,
										r2_top_height_percent=1.0,
										r2_bottom_height_percent=1.0,
										r2_width_multiplier=3.0)

	reg1 = cregion(reg_params1, top_height = 100, bottom_height = 200)

	center_point1 = point.cpoint(300, 500, name="ID_1", index=0)

	reg1.set_center_point(center_point1)

	print(reg1.info_string)

	ep1 = point.cpoint(320, 500, name="Est_1", index=0)
	cost1 = reg1.compute_cost(ep1)
	print('Cost for (%d, %d): %5.2f' % (ep1.x, ep1.y, str(cost1)))

	ep2 = point.cpoint(350, 600, name="Est_2", index=0)
	cost2 = reg1.compute_cost(ep2)
	print('Cost for (%d, %d): %5.2f' % (ep2.x, ep2.y, str(cost2)))

	ep3 = point.cpoint(350, 600, name="Est_3", index=0)
	cost3 = reg1.compute_cost(ep3)
	print('Cost for (%d, %d): %5.2f' % (ep3.x, ep3.y, str(cost2)))

	

	print('Done ...')




# Original (broken) version of is is_this_ep_an_r2_hit

#if ((est_pt.x <= self._r2_x_rhs and est_pt.x >= self._r1_x_rhs) or ) \
			
#			and est_pt.x >= self._r2_x_lhs and est_pt.x <= self._r1_x_lhs \
#			and est_pt.y >= self._r2_y_top and est_pt.y <= self._r1_y_top \
#			and est_pt.y <= self._r2_y_bottom and est_pt.y >= self._r1_y_bottom: