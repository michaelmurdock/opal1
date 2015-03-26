# cost_calculator.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import logging

import utilsLib
import error_parameters as err_params
import region_parameters as reg_params


class ccost_calculator(object):
	'''
	An instance of the ccost_calculator class is used to do the tasks related to calculating the 
	costs for a sequence of origin_point instances that have been processed by the dtw_aligner. 

	Public Methods:

	create_regions_for_origin_points()
	calculate_costs_for_origin_points()



	'''
	def __init__(self, xorigin_points, error_params, region_params, bverbose_mode):
		'''
		'''
		self._xorigin_points = xorigin_points
		self._error_params = error_params
		self._region_params = region_params
		self._bverbose_mode = bverbose_mode


		result = self._introduce_origin_point_neighbors()
		if not result.success:
			raise ValueError("Error returned from _introduce_origin_point_neighbors. Details: " + result.message)


		result = self._set_region_parameters()
		if not result.success:
			raise ValueError("Error returned from _set_region_parameters. Details: " + result.message)


		result = self._set_error_parameters()
		if not result.success:
			raise ValueError("Error returned from _set_error_parameters. Details: " + result.message)


	def _set_region_parameters(self):
		'''
		Private method that iterates through our list of origin_points and sets the
		region_parameters for each one.
		'''
		for op in self._xorigin_points:
			op.set_region_parameters(self._region_params)

		return utilsLib.Result(True,message='', item=None)

	def _set_error_parameters(self):
		'''
		Private method that iterates through our list of origin_points and sets the
		error_parameters for each one.
		'''
		for op in self._xorigin_points:
			op.set_error_parameters(self._error_params)

		return utilsLib.Result(True,message='', item=None)

	def _introduce_origin_point_neighbors(self):
		'''
		'''

		# Iterator through our list of origin_points and tell each op the y-coordinate of its
		# above and below neighbor

		# Do Q0	- Only set its bottom neighbor	
		curr_op = self._xorigin_points[0]
		bottom_op = self._xorigin_points[1]
		curr_op.set_top_neighbor_y(None)
		curr_op.set_bottom_neighbor_y(bottom_op.y)

		for idx in range(1, len(self._xorigin_points)-1):

			# Get the top, current, and bottom origin_points
			top_op = self._xorigin_points[idx-1]
			curr_op = self._xorigin_points[idx]
			bottom_op = self._xorigin_points[idx+1]
		
			# Tell the current origin_point about the top and bottom y coordinates
			curr_op.set_top_neighbor_y(top_op.y)
			curr_op.set_bottom_neighbor_y(bottom_op.y)

		# Do Last Q - Only set its top neighbor
		idx = len(self._xorigin_points)-1
		curr_op = self._xorigin_points[idx]
		top_op = self._xorigin_points[idx-1]
		curr_op.set_top_neighbor_y(top_op.y)

		return utilsLib.Result(True,message='', item=None)


	def create_regions_for_origin_points(self):
		'''
		'''
		for op in self._xorigin_points:
			result = op.create_tolerance_region()
			if not result.success:
				smsg = 'Error returned from create_tolerance_region for origin_point: ' + op.name + ' . Details: ' + result.message
				return utilsLib.Result(False, message=smsg, item=None)

		return utilsLib.Result(True, '', None)

	def calculate_costs_for_origin_points(self):
		for op in self._xorigin_points:
			result = op.calculate_costs()
			if not result.success:
				smsg = 'Error returned from calculate_costs for origin_point: ' + op.name + ' . Details: ' + result.msg
				return utilsLib.Result(False, message=smsg, item=None)
			
		return utilsLib.Result(True, '', None)

	def aggregate_costs_for_origin_points(self):
		total_costs = 0.0
		logging.debug('\nAggregating the costs for each origin_point:')
		for op in self._xorigin_points:
			result = op.get_costs()
			if not result.success:
				smsg = 'Error returned from get_costs for origin_point: ' + op.name + ' . Details: ' + result.msg
				return utilsLib.Result(False, message=smsg, item=None)
			cost = result.item
			total_costs += cost
		return utilsLib.Result(True,'',item=total_costs)

if __name__ == "__main__":

	print('Hello world ... ')

	print('Done')
