# origin_point.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import os
import sys
from types import *

import utilsLib
import point as pt

class cestimate_point(pt.cpoint):
	'''
	cestimate_point is a class derived from the cpoint class. An instance of cestimate_point is used to hold
	the data for an estimate for an origin point.
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
		pt.cpoint.__init__(self, x, y, 'P' + name, index)
		self._xcandidate_origin_points = []
		self._assigned_origin_point = None

	def __repr__(self):
		return repr((self.x, self.y, self.name, self.index))
	
	
	def add_candidate_origin_point(self, origin_point):
		'''
		When the backtrace is being analyzed to create the list of origin_points, each with their
		associated estimate_points, if this estimate_point is assigned to more than one origin_point, 
		then we will need to make a determination as to which origin_point this estimate_point
		belongs (it can't belong to multiple origin_points).
		'''
		self._xcandidate_origin_points.append(origin_point)

	def get_candidate_origin_points(self):
		'''
		'''
		return self._xcandidate_origin_points

	def set_final_origin_point(self, origin_point):
		'''
		'''
		try:
			self._assigned_origin_point = origin_point
			self._xcandidate_origin_points = []
		except:
			smsg = 'Exception thrown in set_final_origin_point. Details: ' + utilsLib.getExceptionDetails()
			return utilsLib.Result(False,message=smsg, item=None)
	
		return utilsLib.Result(True,message='', item=None)

	@property
	def y(self):
		return self._y


	@property
	def num_candidate_origin_points(self):
		'''
		If this list is greater than 1, then it means we have to choose between them and
		keep only the one with the lowest local_cost value.
		'''
		return len(self._xcandidate_origin_points)




if __name__ == "__main__":

	pt1 = cestimate_point(13, 42, "ID_1")
	print(pt1.info_string)

	pt2 = cestimate_point(13, 42, "ID_2", index=0)
	print(pt2.info_string)

	pt3 = cestimate_point(13, 42, name="ID_3", index=0)
	print (pt3.info_string)

	pt4 = cestimate_point(13, 42, index=0)
	pt4.name = "ID_4"
	print (pt4.info_string)

	pt5 = cestimate_point(0, 1, "ID_5")
	pt5.index = 5
	print (pt5.info_string)

	try:
		pt1_bogus = cestimate_point(1.2, 3, "Bogus")
	except AssertionError:
		print('Exception thrown calling the cestimate_point constructor: ' + utilsLib.getExceptionDetails())

	print('Done ...')