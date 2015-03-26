# origin_points.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import utilsLib
import text_line as tl
import origin_point as op
import region
import region_parameters as rp

class corigin_points(object):
	'''
	An instance of the corigin_points list is used to wrap a list of corigin_point instances.
	'''
	def __init__(self, verbose_mode):
		'''
		stuff
		'''
		self._verbose_mode = verbose_mode
		self._xorigin_points = []
		self._zorigin_points = {}

	def read_origin_points(self, mdat_filename):
		'''
		This method uses a ctext_line instance to read the data from an MDAT file. We then copy
		that data into our internal _xorigin_points list.
		'''
		text_lines_container = tl.ctext_lines_container()
		result = text_lines_container.read(mdat_filename)
		if result.success:
			result = text_lines_container.get_text_line_data_list()
			if result.success:
				xtext_lines = result.item
			else:
				return result

			for text_line_data_instance in xtext_lines:
				
				# corigin_point instance from a ctext_line_data instance
				orig_pt = op.corigin_point(text_line_data_instance.x,
										   text_line_data_instance.y,
										   text_line_data_instance.name,
										   text_line_data_instance.index)

				if self._verbose_mode:
					orig_pt.verbose_mode = True
				self._xorigin_points.append(orig_pt)
				self._zorigin_points[orig_pt.name] = orig_pt
		else:
			return result

		return utilsLib.Result(True,message='', item=None)

	def sort_origin_points(self):
		'''
		Sorts the list _xorigin_points (which consists of corigin_point instances) by the origin_point's y coordinate.
		The sorted list is stored in the _xsorted_origin_points list and is accessed with the get_sorted_points method.
		This method returns the Result object indicating success or failure.
		'''
		try:
			self._xsorted_origin_points = sorted(self._xorigin_points, key=lambda x: x.y, reverse=False)
			smsg = ''
			bsuccess = True
		except:
			smsg = 'Exception thrown in sort_origin_points method calling the sorted function. Details: ' + utilsLib.getExceptionDetails()
			bsuccess = False
		return utilsLib.Result(bsuccess,smsg, item=None)


	def get_sorted_points(self):
		'''
		Returns a list of corigin_point instances that are sorted (smallest to largest) by the y value
		'''
		return self._xsorted_origin_points


	def get_points(self):
		'''
		Returns a list of corigin_point instances.
		'''
		return self._xorigin_points

	def get_info_list(self):
		'''
		Returns a list of strings (suitable for printing). Each list element corresponds to a corigin_points's info_string property
		'''
		xInfo = []
		for op in self._xorigin_points:
			xInfo.append(op.info_string)
		return utilsLib.Result(True,message='', item=xInfo)

class cpoint_chooser(object):
	'''
	'''
	def __init__(self):
		'''
		This constructor initializes our list, _xpoints, that will be used to hold
		origin_points that need to be analyzed so as to choose the one with the lowest
		local_cost. After this constructor is called, the client code must call add_point
		for each origin_point that is under consideration. the last step is for the 
		client code to call find_lowest_cost_origin_point, which if successful allows
		the client code to call the get_lowest_cost_origin_point and get_loser_origin_points
		methods.
		
		'''
		self._xpoints = []
		self._lowest_cost_origin_point = None
		self._zlosers = {}

	def add_point(self, orig_point):
		'''
		'''
		self._xpoints.append(orig_point)

	def find_lowest_cost_origin_point(self):
		'''
		Idenitfy the origin_point that was added with add_point that has the lowest local_cost
		This origin_point is stored in self._lowest_cost_origin_point. All of the loser 
		origin_points are stored in the self._zlosers dictionary.
		'''
		# We start by adding all items to the losers dictionary.
		# Then when we fiind the winner we will remove it from the losers dictionary.
		self._zlosers = {}
		for op in self._xpoints:
			self._zlosers[op.name] = op

		# We let the first op in the list be the current best choice
		best_op = self._xpoints[0]

		# Iterate through our list to find the op with the lowest local_cost
		for op in self._xpoints:
			if op.local_cost < best_op.local_cost:
				best_op = op

		# We save away the winner
		self._lowest_cost_origin_point = best_op

		# We remove the winner from the loser list
		del self._zlosers[best_op.name]

		return utilsLib.Result(True,'', item=None)

		
	def get_lowest_cost_origin_point(self):
		'''
		Returns the origin_point that was found as the one with the lowest local_cost in the 
		find_lowest_cost_origin_point method.
		'''
		return utilsLib.Result(True,'', item=self._lowest_cost_origin_point)

	def get_loser_origin_points(self):
		'''
		Creates and returns the list of all the origin_points that were NOT the winner 
		calculated in get_lowest_cost_origin_point.
		'''
		xlosers = []
		try:
			for k in self._zlosers.keys():
				op = self._zlosers[k]
				xlosers.append(op)
		except:
			smsg = 'Exception thrown in get_loser_origin_points. Details: ' + utilsLib.getExceptionDetails()
			return utilsLib.Result(False,smsg, item=None)

		return utilsLib.Result(True,'', item=xlosers)

			
if __name__ == "__main__":

	dataFile1 = r'C:\tmp1\doc2.mdat'
	orig_points = corigin_points()
	result = orig_points.load_origin_points(dataFile1)
	if result.success:
		result = orig_points.get_info_list()
		if result.success:
			xinfo_list = result.item
			for item in xinfo_list:
				print(item)


	print('Done ...')