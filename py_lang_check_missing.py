#!/usr/bin/env python

# Checks for missing strings
# Eliminates unused strings

import sys
from string import *
import os

# --- ------
def gather_english_strings( p_lang_file ):
	global english_strings

	lang_file = open( p_lang_file )
	english_strings = lang_file.readlines()
	lang_file.close()
# --- ------
def process_lang_strings( p_lang_file ):
	global lang_strings, english_strings

	lang_file = open( p_lang_file )
	lang_lines = lang_file.readlines()
	lang_file.close()

	# populate lang_strings
	for i in lang_lines:
		string_key = process_string( i )
		if ( len( string_key ) > 0 ):
			# strip leading whitespace
			lang_strings[string_key] = lstrip(i)

	#lang_file = open( p_lang_file+".new", "w" )
	lang_file = open( p_lang_file, "w" )

	# print header part
	for i in lang_lines:
		if ( found( i, "?>" ) ):
			lang_file.write( i )
			break
		lang_file.write( i )

	header = 0;
	for i in english_strings:
		# skip header for english file
		if ( 0 == header ):
			if ( found( i, "?>" ) ):
				header = 1
		else:
			string_key = process_string( i )
			if (( len( string_key ) > 0 )&( lang_strings.has_key( string_key ) )):
				lang_file.write( lang_strings[string_key] )
			else:
				lang_file.write( i )

	lang_file.close()
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
english_strings = {}
lang_file_list = os.listdir( lang_dir )
lang_file_list.sort()

print "Checking for Missing Strings"
print "Loading: strings_english.txt"
gather_english_strings( lang_dir+"\\strings_english.txt" )
for lang_file in lang_file_list:
	lang_strings = {}
	if (( lang_file != "strings_english.txt" )&( found( lang_file, "txt" ) )):
		print "Processing: "+lang_file
		process_lang_strings( lang_dir+"\\"+lang_file )
