#!/usr/bin/env python

# This reports duplicate strings

import sys
from string import *
import os

# --- ------
def process_lang_strings( p_lang_file ):
	global lang_strings, found_duplicates

	lang_file = open( p_lang_file )
	lang_lines = lang_file.readlines()
	lang_file.close()

	# reports duplicates for each file
	line_number = 0;
	for i in lang_lines:
		line_number = line_number+1
		lang_string = process_string( i )
		if ( len( lang_string ) > 0 ):
			if ( 1 == lang_strings.has_key( lang_string ) ):
				print "DUPLICATE: "+lang_string+" (line #"+str(line_number)+")"
				found_duplicates = 1
				continue
			lang_strings[lang_string] = 1
			match_found = 1
# --- ------
def found( p_string, p_sub_str ):
	if ( -1 != find( p_string, p_sub_str ) ):
		return 1
	else:
		return 0
# --- ------
def process_string( p_string ):
	p_string = translate( p_string, maketrans( "()\\;<>:\".,", "          " ) )
	words = split( p_string )
	for a in words:
		if ( -1 != find( a, "$" ) ):
			return a
	return ""
# --- ------

# ===========================
#             MAIN
# ===========================
lang_dir = os.getcwd()
lang_strings = {}
found_duplicates = 0
lang_file_list = os.listdir( lang_dir )
lang_file_list.sort()

print "Checking for Duplicates"
for lang_file in lang_file_list:
	lang_strings = {}
	found_duplicates = 0
	if ( found( lang_file, ".txt" ) ):
		print "Processing: "+lang_file
		process_lang_strings( lang_dir+"\\"+lang_file )
