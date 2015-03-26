# estimate_points.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import utilsLib
import text_line as tl
import estimate_point as ep


class cestimate_points(object):
	'''
	An instance of the cestimate_points list is used to wrap a list of cestimate_point instances.
	'''
	def __init__(self):
		'''
		stuff
		'''
		self._xestimate_points = []
		self._zestimate_points = {}


	def read_estimate_points(self, mdat_filename):
		'''
		This method uses a ctext_line instance to read the data from an MDAT file. We then copy
		that data into our internal _xestimate_points list.
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
				est_pt = ep.cestimate_point(text_line_data_instance.x,
										   text_line_data_instance.y,
										   text_line_data_instance.name,
										   text_line_data_instance.index)

				self._xestimate_points.append(est_pt)
				self._zestimate_points[est_pt.name] = est_pt
		else:
			return result

		return utilsLib.Result(True,message='', item=None)


	def sort_estimate_points(self):
		'''
		Sorts the list _xestimate_points (which consists of cestimate_point instances) by the estimate_point's y coordinate.
		The sorted list is stored in the _xsorted_estimate_points list and is accessed with the get_sorted_points method.
		This method returns the Result object indicating success or failure.
		'''
		try:
			self._xsorted_estimate_points = sorted(self._xestimate_points, key=lambda x: x.y, reverse=False)
			smsg = ''
			bsuccess = True
		except:
			smsg = 'Exception thrown in sort_estimate_points method calling the sorted function. Details: ' + utilsLib.getExceptionDetails()
			bsuccess = False
		return utilsLib.Result(bsuccess,smsg, item=None)


	def get_points(self):
		'''
		Returns a list of cestimate_point instances.
		'''
		return self._xestimate_points

	def get_sorted_points(self):
		'''
		Returns a list of cestimate_point instances that are sorted (smallest to largest) by the y value
		'''
		return self._xsorted_estimate_points

	def get_info_list(self):
		'''
		Returns a list of strings (suitable for printing). Each list element corresponds to a cestimate_points's info_string property
		'''
		xInfo = []
		for op in self._xestimate_points:
			xInfo.append(op.info_string)
		return utilsLib.Result(True,message='', item=xInfo)



			
if __name__ == "__main__":

	dataFile1 = r'C:\tmp1\doc2.mdat'
	estimate_points = cestimate_points()
	result = estimate_points.read_estimate_points(dataFile1)
	if result.success:
		result = estimate_points.get_info_list()
		if result.success:
			xinfo_list = result.item
			for item in xinfo_list:
				print(item)


	print('Done ...')