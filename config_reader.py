# config_reader.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import logging
from configobj import ConfigObj

import utilsLib
import error_parameters as err_params
import region_parameters as reg_params

class cconfig_reader(object):
	"""description of class"""
	def __init__(self, config_filename):
		'''
		'''
		# Save away the passed-in config filename
		self._config_filename = config_filename

		logging.debug('cconfig_reader constructor: config file: ' + self._config_filename)

		# Create a new CConfigObj instance
		try:
			self._config = ConfigObj(self._config_filename)

		except:
			raise

		# Create the objects to hold the config data
		# Note that these constructors set defaults in case config file is not used
		self._error_parameters = err_params.cerror_parameters()
		self._region_parameters = reg_params.cregion_parameters()

		# Defaults in case config file is not used
		self._verbose_mode = False
		self._sort_estimate_points = False
		self._sort_origin_points = False
		self._results_filename = 'results.txt'

		# Read the Process section
		result = self._read_item('Process', 'sort_estimate_points')
		if result.success:
			self._sort_estimate_points = bool(result.item)
			
		result = self._read_item('Process', 'sort_origin_points')
		if result.success:
			self._sort_origin_points = bool(result.item)
		
		result = self._read_item('Process', 'results_filename')
		if result.success:
			self._results_filename = result.item

		# Read the items in the Logging section
		result = self._read_item('Logging', 'verbose_mode')
		if result.success:
			self._verbose_mode = bool(result.item)

		# Read the items in the Error-Parameters section
		result = self._read_item('Error-Parameters', 'cost_for_miss')
		if result.success:
			self._error_parameters.cost_for_miss = float(result.item)

		result = self._read_item('Error-Parameters', 'cost_per_false_alarm')
		if result.success:
			self._error_parameters.cost_per_false_alarm = float(result.item)

		# Read the items in the Region-Parameters section
		result = self._read_item('Region-Parameters', 'r2_width_is_same_as_r1')
		if result.success:
			self._region_parameters.r2_width_is_same_as_r1 = bool(result.item)

		result = self._read_item('Region-Parameters', 'max_line_height_clamp_factor')
		if result.success:
			self._region_parameters.max_line_height_clamp_factor = float(result.item)

		# Read the items in the Region-1-Parameters section
		result = self._read_item('Region-1-Parameters', 'r1_top_height_percent')
		if result.success:
			self._region_parameters.r1_top_height_percent = float(result.item)

		result = self._read_item('Region-1-Parameters', 'r1_bottom_height_percent')
		if result.success:
			self._region_parameters.r1_bottom_height_percent = float(result.item)

		result = self._read_item('Region-1-Parameters', 'r1_width_multiplier')
		if result.success:
			self._region_parameters.r1_width_multiplier = float(result.item)

		# Read the items in the Region-2-Parameters section
		result = self._read_item('Region-2-Parameters', 'r2_top_height_percent')
		if result.success:
			self._region_parameters.r2_top_height_percent = float(result.item)

		result = self._read_item('Region-2-Parameters', 'r2_bottom_height_percent')
		if result.success:
			self._region_parameters.r2_bottom_height_percent = float(result.item)

		result = self._read_item('Region-2-Parameters', 'r2_width_multiplier')
		if result.success:
			self._region_parameters.r2_width_multiplier = float(result.item)

	def _read_item(self, section_name, item_name):
		val = self._config[section_name][item_name]
		if val:
			return utilsLib.Result(True,message='', item=val)
		else:
			return utilsLib.Result(False,message='Requested item not found', item=None)

	@property
	def error_parameters(self):
		return self._error_parameters

	@property
	def region_parameters(self):
		return self._region_parameters

	@property
	def verbose_mode(self):
		return self._verbose_mode

	@property
	def sort_estimate_points(self):
		return self._sort_estimate_points

	@property
	def sort_origin_points(self):
		return self._sort_origin_points

	@property
	def results_filename(self):
		return self._results_filename


if __name__ == "__main__":

	config_filename = r'C:\tmp10\config1.ini'
	reader = cconfig_reader(config_filename)
	# reader.error_parameters.x
	# reader.region_parameters.x


	# Process Section
	print('Process Section:')
	print('%s'    % reader.sort_estimate_points)
	print('%s'    % reader.sort_origin_points)


	# Logging Section
	print('Logging Section:')
	print('%s'    % reader.verbose_mode)

	# Error-Parameters Section
	print('Error-Parameters Section:')
	print('%5.2f' % reader.error_parameters.cost_for_miss)
	print('%5.2f' % reader.error_parameters.cost_per_false_alarm)
	
	# Region-Parameters Section
	print('Region-Parameters Section:')
	print('%s'    % reader._region_parameters.r2_width_is_same_as_r1)
	print('%s'    % reader._region_parameters.max_line_height_clamp_factor)
	
	# Region-1-Parameters Section
	print('Region-1-Parameters Section:')
	print('%5.2f' % reader._region_parameters.r1_top_height_percent)
	print('%5.2f' % reader._region_parameters.r1_bottom_height_percent)
	print('%5.2f' % reader._region_parameters.r1_width_multiplier)
	
	# Region-2-Parameters Section
	print('Region-2-Parameters Section:')
	print('%5.2f' % reader._region_parameters.r2_top_height_percent)
	print('%5.2f' % reader._region_parameters.r2_bottom_height_percent)
	print('%5.2f' % reader._region_parameters.r2_width_multiplier)		
			
		

	 
	print('Done ...')
