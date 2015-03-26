# utilsLib.py
#
from __future__ import print_function


__author__ = "MichaelMurdock"
__date__ = "$Aug 2, 2010 8:34:58 PM$"

import sys
from types import *


def getExceptionDetails():
	'''
	Returns a string derived from the Exception information in the exc_info object
	'''
	sDetail1 = ''
	if sys.exc_info()[0]:
		sDetail1 = str(sys.exc_info()[0])

	sDetail2 = ''
	if sys.exc_info()[1]:
		sDetail2 = str(sys.exc_info()[1])
	return ' Exception Details: ' + sDetail1 + sDetail2




class Result(object):
	'''
	An instance of this class is typically created as an easy way to return a compound object in a consistent, 
	predictable way across all code.
	'''

	def __init__(self, success=False, message='', item = None):
		assert type(success) is BooleanType, "success is not a boolean: %s" % 'success'
		assert type(message) is StringType, "message is not a string: %s" % 'message'
		self._bSuccess = success
		self._sMessage = message
		self._item = item
		
	def getSuccess(self):
		return self._bSuccess
	def setSuccess(self, bValue):
		self._bSuccess = bValue
	def getMsg(self):
		return self._sMessage
	def setMsg(self,sMsg):
		self._sMessage = sMsg
	def getItem(self):
		return self._item
	def setItem(self,item):
		self._item = item
	success = property(fget=getSuccess, fset=setSuccess, fdel=None, doc='Boolean indicating success or failure')
	message = property(fget=getMsg, fset=setMsg, fdel=None, doc='Error message if success == False')
	item = property(fget=getItem, fset=setItem, fdel=None, doc='Object being returned')

class CEnum(int):
	'''
	Enumeration value is a named integer.
	'''
	#pylint: disable=R0904

	def __new__(cls, rank, name):
		obj = int.__new__(cls, rank)
		obj.name = name
		return obj

	def __repr__(self):
		return 'CEnum(' + repr(int(self)) + ', ' + repr(self.name) + ')'






if __name__ == '__main__':

	


	# ---------------------------Tests of the CResult class ----------------------------
	def myFirstFunction(arg1, arg2):
		return Result(True,'',[arg1, arg2])

	result1 = myFirstFunction('foo', 'bar')
	if result1.success:
		print(result1.item[0] + ' and ' + result1.item[1])

	def mySecondFunction(arg1):
		return Result(False, message = "This function failed for obvious reasons")

	result2 = mySecondFunction('Money, Fame and Glory')
	if not result2.success:
		print("Error Details: " + result2.message)

	# ---------------------------Tests of the Enum class ----------------------------
	# pylint: disable=C0103
	WEAK = CEnum(1, 'WEAK')
	MODERATE = CEnum(2, 'MODERATE')
	STRONG = CEnum(3, 'STRONG')
	assert repr(STRONG) == "CEnum(3, 'STRONG')"
	assert WEAK < MODERATE < STRONG
	assert MODERATE > WEAK
	assert WEAK.name == 'WEAK'
	assert WEAK == 1

	print('Done.')