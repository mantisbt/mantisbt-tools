#!/usr/bin/env python

import sys
from string import *
import os
import time

# FUNCTIONS

# --------------------------------------------------------------------
# --- process_function -----------------------------------------------
# --------------------------------------------------------------------

def process_function( p_source_lines, p_start_pos ):
	total_open_brace = 0

	for i in range( p_start_pos, len( p_source_lines ) ):
		total_open_brace = total_open_brace + count( p_source_lines[i], '{' )
		total_open_brace = total_open_brace - count( p_source_lines[i], '}' )

		if ( find( p_source_lines[i], 'return ') > 0 ):
			return p_source_lines[i]

		if ( total_open_brace == 0 ):
			return ' '

# --------------------------------------------------------------------
# --- process_api_file -----------------------------------------------
# --------------------------------------------------------------------

def process_api_file( p_file_name ):
	global total_lines, function_list

	infile = open( 'mantis/'+p_file_name, 'r' )
	source_lines = infile.readlines()
	infile.close()

	for i in range( len( source_lines ) ):
		source_line = source_lines[i]
		stripped_source_line = strip( source_line )
		# source_line = strip( source_lines[i] )
		if ( find( stripped_source_line, 'function' ) == 0 ):
			open_paren_pos 		= find( stripped_source_line, '(' )
			close_paren_pos 	= find( stripped_source_line, ')' )

			underscore_first 	= find( p_file_name, '_' )+1
			underscore_last 	= rfind( p_file_name, '_' )

			module_name 		= p_file_name[underscore_first:underscore_last]
			function_name 		= stripped_source_line[9:open_paren_pos]
			function_params		= stripped_source_line[open_paren_pos+2:close_paren_pos-1]
			line_number			= i
			return_value		= process_function( source_lines, line_number )

			function_list.append( ( p_file_name,
									module_name,
									function_name,
									function_params,
									line_number,
									return_value ) )

			process_function( source_lines, i )

	total_lines = total_lines + len( source_lines )

# --------------------------------------------------------------------
# --- process_file ---------------------------------------------------
# --------------------------------------------------------------------

def process_file( p_file_name ):
	global function_list, file_function_list

	infile = open( 'mantis/'+p_file_name, 'r' )
	source_lines = infile.readlines()
	infile.close()

	for j in range ( len( function_list ) ):
		function_name = function_list[j][2]
		for i in range( len( source_lines ) ):

			if ( find( source_lines[i], ' '+function_name ) > -1 ):
				file_function_list.append( ( p_file_name, function_name, i ) )
				#print ' '+p_file_name+'('+str( i )+'): \t'+function_name
			if ( find( source_lines[i], '\t'+function_name ) > -1 ):
				file_function_list.append( ( p_file_name, function_name, i ) )

# --------------------------------------------------------------------
# --- print_function_item --------------------------------------------
# --------------------------------------------------------------------

def print_function_item( p_function_item ):
	file_name 		= p_function_item[0]
	module_name 	= p_function_item[1]
	function_name 	= p_function_item[2]
	function_param 	= p_function_item[3]
	line_number 	= p_function_item[4]
	return_value 	= p_function_item[5]

	print_string = '['+module_name+'] ('+str( line_number )+') '+function_name+'()'
	print print_string
	print_string = '  paramcount: '+str( len(  split( strip( function_param ), ' ' ) ) )
	print print_string
	if ( len( strip( return_value ) ) > 0 ):
		print '  return value: ' + strip( return_value )
	#print_function_parameters( function_param )

# --------------------------------------------------------------------
# --- print_function_parameters --------------------------------------
# --------------------------------------------------------------------

def print_function_parameters( p_function_parameters ):
	if ( len( p_function_parameters ) > 0 ):
		param_list = split( p_function_parameters, ' ' )

		for i in range( len( param_list ) ):
			comma_pos = find( param_list[i], ',' )
			if ( comma_pos > 0 ):
				print "   "+param_list[i][:comma_pos]
			else:
				print "   "+param_list[i]
	else:
		print "NO PARAMETERS"
	print "--------------------------"

# --------------------------------------------------------------------
# --- print_function_counts ------------------------------------------
# --------------------------------------------------------------------

def print_function_counts():
	global  function_count_list

	keys = function_count_list.keys()
	keys.sort()
	for i in range ( len( keys ) ):
		if ( function_count_list[keys[i]] > 0 ):
			print keys[i]+'\t'+str( function_count_list[keys[i]] )

# --------------------------------------------------------------------
# --- tally_function_counts ------------------------------------------
# --------------------------------------------------------------------

def tally_function_counts():
	global function_list, file_function_list, function_count_list

	# build map # use -1 since we want to discount the definition
	for i in range( len( function_list ) ):
		function_list_key = function_list[i][2]
		function_count_list[function_list_key] = -1

	# process functions and file_function
	for j in range( len( file_function_list ) ):
		file_function_name = file_function_list[j][1]

		if ( file_function_name == 'email_close' ):
			print file_function_list[j][0]
			print file_function_list[j][1]
			print file_function_list[j][2]

		function_count_list[file_function_name] = function_count_list[file_function_name] + 1

# --------------------------------------------------------------------
# --- GLOBAL VARIABLES -----------------------------------------------
# --------------------------------------------------------------------

# file_name, module_name, function_name, function_params, line_number, return_value
function_list = []			# info for each function
# file_name, function_name, line number
file_function_list = []		# functions found in each file
# function_name, count
function_count_list = {}	# contains counts occurances of functions
total_lines = 0

# --------------------------------------------------------------------
# --- MAIN -----------------------------------------------------------
# --------------------------------------------------------------------

dir_list = os.listdir( "mantis" )
dir_list.sort()
for i in range( len( dir_list ) ):
	file_name = dir_list[i]
	if ( find( file_name, 'core_' ) != -1 ):
		print "Processing: "+file_name;
		process_api_file( file_name )

for i in range( len( function_list ) ):
	function_item 	= function_list[i]
	#print_function_item( function_item )

print len( function_list )
print total_lines

dir_list = os.listdir( "mantis" )
dir_list.sort()
for i in range( len( dir_list ) ):
	file_name = dir_list[i]
	if ( find( file_name, 'php' ) != -1 ):
		print "Processing: "+file_name;
		process_file( file_name )

tally_function_counts()
print_function_counts()

# --------------------------------------------------------------------
# --- END ------------------------------------------------------------
# --------------------------------------------------------------------