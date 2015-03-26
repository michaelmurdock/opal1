# Driver.py
from __future__ import print_function
import math
import sys
import logging


import origin_points as op
import estimate_points as ep
import region_parameters as rp
import error_parameters as err_params
import config_reader as config
import utilsLib
import cost_info as ci
import dtw_aligner
import cost_calculator as cc


bVerbose_mode = True


# create logger
logging.basicConfig(filename='opal.log', level=logging.DEBUG, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                    




# ---------------- Test Data (T2a) ---------------------
#op_data_file = r'C:\test2\test2a\s1_08_gt.mdat'
#ep_data_file = r'C:\test2\test2a\s1_08_ep1_orange.mdat'


# ---------------- Test Data (T2b) ---------------------
op_data_file = r'C:\test2\test2b\s1_08_gt.mdat'
ep_data_file = r'C:\test2\test2b\s1_08_ep2_yellow.mdat'


logging.debug('Starting opal session.')
logging.debug('origin_points: ' + op_data_file)
logging.debug('estimate_points: ' + ep_data_file)
			
if __name__ == "__main__":

	# Read all configuration paramters from a config.ini file and populate a cconfig_reader 
	# object with these parameters, which we then pass into whatever objects require this data. 
	config_filename = r'C:\tmp10\config1.ini'
	logging.debug('Config file: ' + config_filename)
	reader = config.cconfig_reader(config_filename)

	# Origin Points (ground truth) are loaded from an MDAT file
	orig_points = op.corigin_points()
	read_result = orig_points.read_origin_points(op_data_file)
	if read_result.success:
		
		# If it's turned on in the config.ini file, sort the OPs on their y coordinates
		if reader.sort_origin_points:
			result = orig_points.sort_origin_points()
			if result.success:
				# Get the _sorted_ OP sequence to pass into the dtw_aligner
				xorig_points = orig_points.get_sorted_points()
			else:
				logging.error('Error in sort_origin_points(). Details: ' + result.message)
				exit()
		else:
			# Get the _non-sorted_ OP sequence to pass into the dtw_aligner
			xorig_points = orig_points.get_points()
			
		if reader.verbose_mode:
			if reader.sort_origin_points:
				logging.debug('Origin Points (sorted on y coordinate): ')
				for op in xorig_points:
					logging.debug(op.info_string)
	else:
		logging.error('Error in read_origin_points method. Details: ' + read_result.message)
		exit()



	# Estimate Points are loaded from an MDAT file
	est_points = ep.cestimate_points()
	read_result = est_points.read_estimate_points(ep_data_file)
	if read_result.success:
		
		# If it's turned on in the config.ini file, sort the EPs on their y coordinates
		if reader.sort_estimate_points:
			result = est_points.sort_estimate_points()
			if result.success:
				# Get the _sorted_ EP sequence to pass into the dtw_aligner
				xest_points = est_points.get_sorted_points()
			else:
				logging.error('Error in sort_estimate_points(). Details: ' + read_result.message)
				exit()
		else:
			# Get the _non-sorted_ EP sequence to pass into the dtw_aligner
			xest_points = est_points.get_points()
			
		if reader.verbose_mode:
			if reader.sort_estimate_points:
				logging.debug('\n\nEstimate Points (sorted on y coordinate): ')
				for ep in xest_points:
					logging.debug(ep.info_string)
	else:
		logging.error('Error in read_estimate_points method. Details: ' + result.message)
		exit()


	try:
		bprint_to_screen = True
		aligner = dtw_aligner.dtw_aligner(xorig_points, xest_points, reader.verbose_mode, bprint_to_screen)
	except:
		logging.error('Exception thrown in dtw_aligner constructor. Details: ' + utilsLib.getExceptionDetails())
		exit()
		

	# Look at distances between points in the two sequences
	if reader.verbose_mode:
		for iRow in xrange(0, len(aligner._Q)):
			logging.debug('\nRow: ' + str(iRow))
			for iCol in xrange(0, len(aligner._P)):
				p1 = aligner._Q[iRow]
				p2 = aligner._P[iCol]
				d = aligner._distance(p1, p2)
				logging.debug('Distance between (%d, %d) and (%d, %d): %f' % (p1.x, p1.y, p2.x, p2.y, d))

	try:
		result = aligner.create_empty_cost_matrix()
		if not result.success:
			logging.error('Error returned from aligner.create_empty_cost_matrix(). Details: ' + result.message)
	except:
		logging.error('Exception thrown in dtw_aligner.create_empty_cost_matrix method. Details: ' + utilsLib.getExceptionDetails())
		exit()

	try:
		result = aligner.create_empty_cost_info_matrix()
		if not result.success:
			logging.error('Error returned from aligner.create_empty_choices_matrix(). Details: ' + result.message)
			exit()
	except:
		logging.error('Exception thrown in dtw_aligner.create_empty_choices_matrix method. Details: ' + utilsLib.getExceptionDetails())
		exit()
		

	# Compute the cost matrix
	result = aligner.compute_cost()
	if not result.success:
		logging.error('Error returned from aligner.compute_cost(). Details: ' + result.message)
		exit()

	if reader.verbose_mode:
		fCost = aligner.get_global_cost()
		logging.debug("\n\nGlobal Cost: " + str(fCost))
		aligner.print_cost_matrix()
		aligner.print_cost_info_matrix()

	# Compute the minimum-cost path back through the cost matrix
	result = aligner.get_backtrace()
	if not result.success:
		logging.error('Error returned from aligner.get_backtrace(). Details: ' + result.message)
		exit()
	
	# Process the backtrace to associate estimate_points with origin_points
	result = aligner.process_backtrace()
	if result.success:
		result = aligner.post_process_origin_points()
		if not result.success:
			logging.error('Error returned from aligner.post_process_origin_points(). Details: ' + result.message)
			exit()
	
	# We now have a list of origin_points that each have their _zestimate_points dictionary populated.
	# If there are multiple entries, all but one is a false alarm.
	# If there are no entries we have a miss.
	# We now need to tell each origin_point to score itself.

	
	logging.debug('\n\nestimate_points (P) associated with each origin_point (Q):\n')
	for op in xorig_points:
		logging.debug(op.get_estimate_points_string())
	
		
	# Create the cost_calculator with our dtw-algigned and processed list of origin_points
	try:
		cost_calculator = cc.ccost_calculator(xorig_points, reader.error_parameters, reader.region_parameters, reader.verbose_mode)
	except:
		logging.error('Exception thrown in cost_calculator constructor. Details: ' + utilsLib.getExceptionDetails())
		exit()

	result = cost_calculator.create_regions_for_origin_points()
	if not result.success:
		logging.error('Error returned from cost_calculator.create_regions_for_origin_points(). Details: ' + result.message)
		exit()

	result = cost_calculator.calculate_costs_for_origin_points()
	if result.success:
		result = cost_calculator.aggregate_costs_for_origin_points()
		if result.success:
			total_cost = result.item
			logging.debug('Total cost: %5.2f' % (total_cost))


		
	
	
		
	print ("Done ...")