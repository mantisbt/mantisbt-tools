#!/usr/bin/env python

# This file checkes the filename lengths of all files in a directory.
# Any files over 32 characters in length must be shortened.

import sys
from string import *
import os

# --- ------
def gather_lang_strings( p_lang_file ):
	global lang_strings

	lang_file = open( p_lang_file )
	lang_lines = lang_file.readlines()
	lang_file.close()

	for i in lang_lines:
		lang_string = process_string( i )
		if ( len( lang_string ) > 0 ):
			lang_strings[lang_string] = 1
# --- ------
def gather_php_strings( p_php_file ):
	global php_strings

	php_file = open( p_php_file )
	php_lines = php_file.readlines()
	php_file.close()

	for i in php_lines:
		p_string = translate( i, maketrans( "()\\;<>:\".,", "          " ) )
		words = split( p_string )
		for a in words:
			if ( found( a, "$s_" ) ):
				php_strings[a] = 1
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
def process_string( p_string ):
	p_string = translate( p_string, maketrans( "()\\;<>:\".,", "          " ) )
	words = split( p_string )
	for a in words:
		if ( -1 != find( a, "$s_" ) ):
			return a
	return ""
# --- ------
def process_string_file( p_lang_file ):
	global lang_strings, php_strings

	lang_keys = lang_strings.keys()
	lang_keys.sort()
	php_keys = php_strings.keys()
	php_keys.sort()

	lang_file = open( p_lang_file )
	lang_lines = lang_file.readlines()
	lang_file.close()
	lang_file = open( p_lang_file+".new", "w" )
	for i in lang_lines:
		lang_string = process_string( i )
		if ( len( lang_string ) > 0 ):
			if ( lang_string not in php_keys ):
				#print lang_string
				continue
		lang_file.write( i )
	lang_file.close()
# --- ------
def init():
	global lang_file_list, php_file_list, lang_dir

	php_directory = ".";
	if ( len(sys.argv) < 2 ):
		php_file_list = os.listdir( php_directory )
	elif ( 2 == len(sys.argv) ):
		php_file_list.append( sys.argv[1] )
	else:
		print "ERROR in program arguments"
		sys.exit(1)

	lang_file_list = os.listdir( lang_dir )
# --- ------

# ===========================
#             MAIN
# ===========================
lang_dir = "/home/www/mantis/lang/"
lang_file_list = []
php_file_list = []

php_strings = {}
lang_strings = {}
# --- ------

init()
print "Pre Processing Files"
for php_file in php_file_list:
	if ( found( php_file, ".php" ) ):
		gather_php_strings( php_file )

#lang_file_list = ["strings_english.txt"]
for lang_file in lang_file_list:
	lang_strings = {}
	if ( found( lang_file, ".txt" ) ):
		print "Processing File: "+lang_file
		gather_lang_strings( lang_dir+lang_file )
		process_string_file( lang_dir+lang_file )