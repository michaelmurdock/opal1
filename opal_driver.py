# opal_driver.py
#
from __future__ import print_function

import math
import sys
import getopt
import logging

import origin_points
import estimate_points
import region_parameters as rp
import error_parameters as err_params
import config_reader as config
import utilsLib
import cost_info as ci
import dtw_aligner
import cost_calculator as cc


def main(argv):
	'''
	This is the main driver function for the opal application.
	The command-line arguments specify the files containing the origin_points (ground truth),
	the estimate_points, and the config.ini.
	'''
	origin_point_file = ''
	estimate_point_file = ''
	config_file = ''
	try:
	   opts, args = getopt.getopt(argv,"c:e:o:h",["cfile=","estfile=","origfile=","help"])
	except getopt.GetoptError:
		print('opal_driver.py -c <config_file> -o <origin_point_file> -e <estimate_point_file>')
		sys.exit(2)
		
	for opt, arg in opts:
		if opt == '-h':
			print('opal_driver.py -c <config_file> -o <origin_point_file> -e <estimate_point_file>')
			sys.exit()
		elif opt in ("-c", "--cfile"):
			config_file = arg
		elif opt in ("-o", "--origfile"):
			origin_point_file = arg
		elif opt in ("-e", "--estfile"):
			estimate_point_file = arg
		else:
			print('opal_driver.py -c <config_file> -o <origin_point_file> -e <estimate_point_file>')
			sys.exit(2)
			
	# create logger
	log_file = 'opal.log'
	logging.basicConfig(filename=log_file, level=logging.DEBUG, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	
	logging.debug('Starting opal session.')
	logging.debug('Config file is ' + config_file)
	logging.debug('Origin_point file is ' + origin_point_file)
	logging.debug('Estimate_point file is ' + estimate_point_file)

	# ---------------- Test Data (T2a) ---------------------
	#op_data_file = r'C:\test2\test2a\s1_08_gt.mdat'
	#ep_data_file = r'C:\test2\test2a\s1_08_ep1_orange.mdat'
	
	
	# ---------------- Test Data (T2b) ---------------------
	#op_data_file = r'C:\test2\test2b\s1_08_gt.mdat'
	#logging.debug('origin_points: ' + op_data_file)

	#ep_data_file = r'C:\test2\test2b\s1_08_ep2_yellow.mdat'
	#logging.debug('estimate_points: ' + ep_data_file)

	# Read all configuration paramters from a config.ini file and populate a cconfig_reader 
	# object with these parameters, which we then pass into whatever objects require this data. 
	#config_filename = r'C:\tmp10\config1.ini'
	config_filename = config_file
	logging.debug('Config file: ' + config_filename)
	try:
		reader = config.cconfig_reader(config_filename)
	except:
		smsg = 'Exception thrown calling config.cconfig_reader. Details: ' + utilsLib.getExceptionDetails()
		logging.error(smsg)
		sys.exit(2)

	# Origin Points (ground truth) are loaded from an MDAT file
	orig_points = origin_points.corigin_points(reader.verbose_mode)
	read_result = orig_points.read_origin_points(origin_point_file)
	if read_result.success:
		
		# If it's turned on in the config.ini file, sort the OPs on their y coordinates
		if reader.sort_origin_points:
			result = orig_points.sort_origin_points()
			if result.success:
				# Get the _sorted_ OP sequence to pass into the dtw_aligner
				xorig_points = orig_points.get_sorted_points()
			else:
				logging.error('Error in sort_origin_points(). Details: ' + result.message)
				sys.exit(2)
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
		sys.exit(2)



	# Estimate Points are loaded from an MDAT file
	est_points = estimate_points.cestimate_points()
	read_result = est_points.read_estimate_points(estimate_point_file)
	if read_result.success:
		
		# If it's turned on in the config.ini file, sort the EPs on their y coordinates
		if reader.sort_estimate_points:
			result = est_points.sort_estimate_points()
			if result.success:
				# Get the _sorted_ EP sequence to pass into the dtw_aligner
				xest_points = est_points.get_sorted_points()
			else:
				logging.error('Error in sort_estimate_points(). Details: ' + read_result.message)
				sys.exit(2)
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
		sys.exit(2)


	try:
		bprint_to_screen = True
		aligner = dtw_aligner.dtw_aligner(xorig_points, xest_points, reader.verbose_mode, bprint_to_screen)
	except:
		logging.error('Exception thrown in dtw_aligner constructor. Details: ' + utilsLib.getExceptionDetails())
		sys.exit(2)
		

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
		sys.exit(2)

	try:
		result = aligner.create_empty_cost_info_matrix()
		if not result.success:
			logging.error('Error returned from aligner.create_empty_choices_matrix(). Details: ' + result.message)
			sys.exit(2)
	except:
		logging.error('Exception thrown in dtw_aligner.create_empty_choices_matrix method. Details: ' + utilsLib.getExceptionDetails())
		sys.exit(2)
		

	# Compute the cost matrix
	result = aligner.compute_cost()
	if not result.success:
		logging.error('Error returned from aligner.compute_cost(). Details: ' + result.message)
		sys.exit(2)

	if reader.verbose_mode:
		fCost = aligner.get_global_cost()
		logging.debug("\n\nGlobal Cost: " + str(fCost))
		aligner.print_cost_matrix()
		aligner.print_cost_info_matrix()

	# Compute the minimum-cost path back through the cost matrix
	result = aligner.get_backtrace()
	if not result.success:
		logging.error('Error returned from aligner.get_backtrace(). Details: ' + result.message)
		sys.exit(2)
	
	# Process the backtrace to associate estimate_points with origin_points
	result = aligner.process_backtrace()
	if result.success:
		result = aligner.post_process_origin_points()
		if not result.success:
			logging.error('Error returned from aligner.post_process_origin_points(). Details: ' + result.message)
			return
	
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
		return

	result = cost_calculator.create_regions_for_origin_points()
	if not result.success:
		logging.error('Error returned from cost_calculator.create_regions_for_origin_points(). Details: ' + result.message)
		return


	f = open(reader.results_filename, 'a')
	

	result = cost_calculator.calculate_costs_for_origin_points()
	if result.success:
		result = cost_calculator.aggregate_costs_for_origin_points()
		if result.success:
			total_cost = result.item
			logging.debug('Total cost: %5.2f' % (total_cost))
			f.write('Estimates: %s -- Total Calculated Cost: %5.2f' % (estimate_point_file, total_cost))
			f.close()
		else:
			logging.debug('Error returned from cost_calculator.aggregate_costs_for_origin_points. Details: ' + result.message)
			f.write('Estimates: %s -- Error processing this estimates file. Details: %s\n' % (result.message))
			f.close()

			
if __name__ == "__main__":
	
	main(sys.argv[1:])
	sys.exit(2)
