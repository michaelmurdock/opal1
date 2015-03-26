# text_line.py
# 
from __future__ import print_function

__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"


import os
import sys
from types import *
import csv

import point as pt
import utilsLib


class ctext_line_data(object):
	'''
	An instance of the ctext_line_data class contains the data for a single text-line instance.
	Currently, this class only provides for the location (and an ID or name) for the origin point
	of the text-line segment.
	'''
	def __init__(self, x=-1, y=-1, name='', index=-1):
		assert type(x)			is IntType, "x is not an integer: %s" % str(x)
		assert type(y)			is IntType, "y is not an integer: %s" % str(y)
		assert type(name)		is StringType, "name is not a string: %s" % name
		assert type(index)		is IntType, "index is not an integer: %s" % str(index)
		self._x = x
		self._y = y
		self._name = name
		self._index = index

	@property
	def x(self):
		return self._x

	@x.setter
	def x(self, x):
		self._x = x

	@property
	def y(self):
		return self._y

	@y.setter
	def y(self, y):
		self._y = y

	@property
	def name(self):
		return self._name
	
	@name.setter
	def name(self, name):
		self._name = name

	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, index):
		self._index = index



	@property
	def info_string(self):
		return 'Item Name: %s, Location: (x = %d, y = %d), Index: %d' % (self.name, self.x, self.y, self.index)

	def get_data(self):
		'''
		Returns a list containing x, y, name, and index (in that order)
		'''
		return [self.x, self.y, self.name, self.index]


class ctext_lines_container(object):
	'''
	An instance of the ctext_lines_container class contains the data for a list of ctext_line_data instances.
	'''
	def __init__(self):
		self._xtext_lines = []
		self._ztext_lines = {}
		

	def read(self, mdat_filename):
		'''
		Read the specified file containing comma-separated elements - One line corresponds to one ctext_line_data object.
		Order of the elements: 
			name		: string	:	required	: default=N/A
			x			: integer	:	required	: default=N/A
			y			: integer	:	requried	: default=N/A

		This method returns the usual utilsLib.Result object to indicate success or failure. 
		The ctext_line_data objects can be obtained by calling the get_names() and get_text_line_data() methods.
		'''
		try:
			f = open(mdat_filename, 'rt')
		except:
			sMsg = 'Error attempting to open: ' + mdat_filename + ' ' + utilsLib.getExceptionDetails()
			return utilsLib.Result(False, message=sMsg, item=None)

		try:
			reader = csv.reader(f)
		except:
			sMsg = 'Error reading file: ' + mdat_filename + utilsLib.getExceptionDetails()
			f.close()
			return utilsLib.Result(False, message=sMsg, item=None)

		# We read each row in the file and create a dictionary entry for each row, keyed on its name (ID in the MDAT file)
		index = 0
		for row in reader:
			try:
				numItems = len(row)
				sname = row[0]
				sx = row[1]
				sy = row[2]
			except:
				sMsg = 'Error extracting a row from the file: ' + mdat_filename + ' Details: ' + utilsLib.getExceptionDetails()
				f.close()
				return utilsLib.Result(False, message=sMsg, item=None)

			try:
				one_text_line_data_instance = ctext_line_data(int(sx), int(sy), sname, index)
			except:
				sMsg = 'Error creating a ctext_line_data instance from the values read from file: ' + mdat_filename + utilsLib.getExceptionDetails()
				f.close()
				return utilsLib.Result(False, message=sMsg, item=None) 

			# Add this ctext_line_data object to our internal list and our internal dictionary
			self._xtext_lines.append(one_text_line_data_instance)
			self._ztext_lines[sname] = one_text_line_data_instance
			
			# We use this counter to supply an index to the ctext_line_data constructor, just in case we decide we care about its order
			index += 1
			 
		# Close the file and return the Result instance indicating success
		f.close()
		return utilsLib.Result(True, message='', item=None)

	def get_names(self):
		'''
		Returns (using the Result class) the list of the names of each ctext_line_data object.
		'''
		xnames = []
		for text_line_data in self._xtext_lines:
			xnames.append(text_line_data.name)
		return utilsLib.Result(True, message='', item=xnames)

	def get_text_line_data_instance(self, name):
		'''
		Returns (using the Result class) the ctext_line_data instance for the specified name.
		'''
		try:
			text_line_data = self._ztext_lines[name]
			return utilsLib.Result(True,message='', item=text_line_data)
		except:
			sMsg = 'Exception thrown trying to get the text_line_data object for key: ' + name + utilsLib.getExceptionDetails()
			return utilsLib.Result(False, message=sMsg, item=None)

	def get_text_line_data_list(self):
		'''
		Returns (using the Result class) the list of ctext_line_data instances.
		'''
		return utilsLib.Result(True,message='', item=self._xtext_lines)

if __name__ == "__main__":

	# Create the container for the ctext_line_data objects we are going to create by reading the MDAT file
	text_lines = ctext_lines_container()
	
	# Read the CSV file containing the data for one text_line_data instance per line.
	# Calling the read method results in our internal list and dictionary to be populated with the
	# data in the CSV file. 
	dataFile1 = r'C:\tmp1\doc2.mdat'
	result = text_lines.read(dataFile1)
	if result.success:

		# Method #1 for getting ctext_line_data instances
		result = text_lines.get_names()
		if result.success:
			xnames = result.item
			for name in xnames:
				result = text_lines.get_text_line_data_instance(name)
				if result.success:
					text_line_data = result.item
					print(text_line_data.info_string)
				else:
					print('Error calling get_text_line_data_instance method on Name: ' + name + ' Details: ' + result.message)
		else:
			print('Error calling get_names method. Details: ' + result.message)

		# Method #2 for getting ctext_line_data instances
		result = text_lines.get_text_line_data_list()
		if result.success:
			xtext_line_data = result.item
			for text_line_data_instance in xtext_line_data:
				print(text_line_data_instance.info_string)

	else:
		print('Error calling the read method. Details: ' + result.message)
		
	print('Done ... ')



