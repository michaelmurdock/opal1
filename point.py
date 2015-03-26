# point.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import os
import sys
from types import *

import utilsLib

class cpoint(object):
	'''
	An instance of the cpoint class is a wrapper for the data for an Origin Point of 
	a Text-Line segment in a paragraph of text.

	A point instance contains the following data items:
		x			: integer	:	required	: default=N/A
		y			: integer	:	requried	: default=N/A
		name		: string	:	optional	: default=N/A
		index		: integer	:	optional	: default=-1

	Client code calls the constructor with the (x, y) coordinates and the optional name
	and index values and then can reference these values as instance properties. After calling 
	the constructor, the client code can set the name and index properties.
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
		
		self._x = x
		self._y = y
		self._name = name
		self._index = index

		self._vertical_distance_to_top_neighbor = None
		self._vertical_distance_to_bottom_neighbor = None


	@property
	def info_string(self):
		return self.name + ',  x: ' +  self.sx + ', y: ' + self.sy + ', Index: ' + str(self.index)

	@property
	def x(self):
		return self._x

	@property
	def sx(self):
		return str(self._x)

	@property
	def y(self):
		return self._y

	@property
	def sy(self):
		return str(self._y)

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, name):
		'''
		Set the (string) name value for this Origin Point.
		'''
		assert type(name) is StringType, "name is not a string: %s" % name
		self._name = name

	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, idx):
		'''
		Sets the (integer) index value for this Origin Point.
		'''
		assert type(idx) is IntType, "idx is not an integer: %s" % str(idx)
		self._index = idx

	@property
	def vertical_distance_to_top_neighbor(self, top_neighbor_point):
		'''
		calculates and saves the vertical distance from the specified cpoint instance to this instance.
		'''
		self._vertical_distance_to_top_neighbor = self.y - top_neighbor_point.y

	@vertical_distance_to_top_neighbor.setter
	def vertical_distance_to_top_neighbor(self):
		'''
		returns the vertical distance to the top neighbor
		'''
		return self._vertical_distance_to_top_neighbor

	@property
	def vertical_distance_to_bottom_neighbor(self, bottom_neighbor_point):
		'''
		calculates and saves the vertical distance from the specified cpoint instance to this instance.
		'''
		self._vertical_distance_to_bottom_neighbor = self.y - bottom_neighbor_point.y

	@vertical_distance_to_bottom_neighbor.setter
	def vertical_distance_to_bottom_neighbor(self):
		'''
		returns the vertical distance to the bottom neighbor
		'''
		return self._vertical_distance_to_bottom_neighbor

if __name__ == "__main__":

	pt1 = cpoint(13, 42, "ID_1")
	print(pt1.info_string)

	pt2 = cpoint(13, 42, "ID_2", index=0)
	print(pt2.info_string)

	pt3 = cpoint(13, 42, name="ID_3", index=0)
	print (pt3.info_string)

	pt4 = cpoint(13, 42, index=0)
	pt4.name = "ID_4"
	print (pt4.info_string)

	pt5 = cpoint(0, 1, "ID_5")
	pt5.index = 5
	print (pt5.info_string)

	try:
		pt1_bogus = cpoint(1.2, 3, "Bogus")
	except AssertionError:
		print('Exception thrown calling the cpoint constructor: ' + utilsLib.getExceptionDetails())

	print('Done ...')