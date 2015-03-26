# error_parameters.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import utilsLib


class cerror_parameters(object):
	"""description of class"""
	def __init__(self, cost_for_miss=-1.0, cost_per_false_alarm=-1.0):
		'''
		'''
		self._cost_for_miss=cost_for_miss
		self._cost_per_false_alarm = cost_per_false_alarm

	@property
	def cost_for_miss(self):
		return self._cost_for_miss

	@cost_for_miss.setter
	def cost_for_miss(self, cost):
		self._cost_for_miss = cost

	@property
	def cost_per_false_alarm(self):
		return self._cost_per_false_alarm

	@cost_per_false_alarm.setter
	def cost_per_false_alarm(self, cost):
		self._cost_per_false_alarm = cost


