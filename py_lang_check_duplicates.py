# /usr/bin/env python

# This file checkes the filename lengths of all files in a directory.
# Any files over 32 characters in length must be shortened.

import sys
from string import *
import os

# --- ------
def process_lang_strings( p_lang_file ):
	global lang_strings, found_duplicates

	lang_file = open( p_lang_file )
	lang_lines = lang_file.readlines()
	lang_file.close()

	lang_file = open( p_lang_file+".new", "w" )
	for i in lang_lines:
		lang_string = process_string( i )
		if ( len( lang_string ) > 0 ):
			if ( 1 == lang_strings.has_key( lang_string ) ):
				print "DUPLICATE: "+lang_string
				found_duplicates = 1
				continue
			lang_strings[lang_string] = 1
			match_found = 1
		lang_file.write( i )
	lang_file.close()

	# if there are no duplcaites then remove the .new file
	if ( 0 == found_duplicates ):
		os.system( 'rm ' + p_lang_file+".new" )
# --- ------
def found( p_string, p_sub_str ):
	if ( -1 != find( p_string, p_sub_str ) ):
		return 1
	else:
		return 0
# --- ------
def remove_used_strings():
	global string_count_list

	keys = string_count_list.keys()
	keys.sort()
	for i in keys:
		if ( string_count_list[i] > 0 ):
			del( string_count_list[i] )

# --- ------
# GOOD
def process_string( p_string ):
	p_string = translate( p_string, maketrans( "()\\;<>:\".,", "          " ) )
	words = split( p_string )
	for a in words:
		if ( -1 != find( a, "$s_" ) ):
			return a
	return ""
# --- ------
def init():
	global lang_file_list, lang_dir

	lang_file_list = os.listdir( lang_dir )
	lang_file_list.sort()
# --- ------

# ===========================
#             MAIN
# ===========================
lang_dir = "/home/www/mantis/lang/"
lang_file_list = []
lang_strings = {}
found_duplicates = 0
# --- ------

init()
#lang_file_list = ["strings_english.txt"]
for lang_file in lang_file_list:
	lang_strings = {}
	found_duplicates = 0
	if ( found( lang_file, ".txt" ) ):
		print "Processing: "+lang_file
		process_lang_strings( lang_dir+lang_file )
