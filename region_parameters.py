# region_parameters.py
#
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import utilsLib


class cregion_parameters(object):
	'''
	description of class
	'''
	def __init__(self, 
				r1_top_height_percent=0.0,
				r1_bottom_height_percent=0.0,
				r1_width_multiplier=0.0,
				r2_top_height_percent=0.0,
				r2_bottom_height_percent=0.0,
				r2_width_multiplier=0.0,
				r2_width_is_same_as_r1=False,
				max_line_height_clamp_factor=3.0):
		'''
		Lorem, Ipsum, ...
		'''
		self._r1_top_height_percent = r1_top_height_percent
		self._r1_bottom_height_percent = r1_bottom_height_percent
		self._r1_width_multiplier = r1_width_multiplier

		self._r2_top_height_percent = r2_top_height_percent
		self._r2_bottom_height_percent = r2_bottom_height_percent
		self._r2_width_multiplier = r2_width_multiplier

	def doSomething(self, foo):
		return True

	@property
	def r1_top_height_percent(self):
		return self._r1_top_height_percent

	@r1_top_height_percent.setter
	def r1_top_height_percent(self, val):
		self._r1_top_height_percent = val


	@property
	def r1_bottom_height_percent(self):
		return self._r1_bottom_height_percent

	@r1_bottom_height_percent.setter
	def r1_bottom_height_percent(self, val):
		self._r1_bottom_height_percent = val


	@property
	def r1_width_multiplier(self):
		return self._r1_width_multiplier

	@r1_width_multiplier.setter
	def r1_width_multiplier(self, val):
		self._r1_width_multiplier = val


	@property
	def r2_top_height_percent(self):
		return self._r2_top_height_percent

	@r2_top_height_percent.setter
	def r2_top_height_percent(self, val):
		self._r2_top_height_percent = val


	@property
	def r2_bottom_height_percent(self):
		return self._r2_bottom_height_percent

	@r2_bottom_height_percent.setter
	def r2_bottom_height_percent(self, val):
		self._r2_bottom_height_percent = val


	@property
	def r2_width_multiplier(self):
		return self._r2_width_multiplier

	@r2_width_multiplier.setter
	def r2_width_multiplier(self, val):
		self._r2_width_multiplier = val