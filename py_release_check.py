#!/usr/bin/env python

# This file checkes the filename lengths of all files in a directory.
# Any files over 32 characters in length must be shortened.

import sys
from string import *
import os

# --- ------
# GOOD
def process_string( p_string ):
	p_string = translate( p_string, maketrans( "#()\\;<>:\"\'.,", "            " ) )
	words = split( p_string )
	for a in words:
		if (( -1 != find( a, "$g_" ) )&
			( -1 == find( p_string, "$HTTP_COOKIE_VARS" ) )&
			( -1 == find( p_string, "_include_" ) )&
			( -1 == find( p_string, "_cookie" ) )&
			( -1 == find( p_string, "_enum_" ) )&
			( -1 == find( p_string, "_color" ) )&
			( -1 == find( p_string, "g_html_tags" ) )&
			( -1 == find( p_string, "g_language_choices_arr" ) )&
			( -1 == find( p_string, "g_db_table_prefix" ) )&
			( -1 == find( p_string, "_path" ) )):
			return a
	return ""
# --- ------

# ===========================
#             MAIN
# ===========================
config_file = "/home/www/mantis/config_inc.php"
py_release_file = "/home/www/py_release.py"
config_list = []
py_release_list = []
config_strings = {}
py_release_strings = {}

# open config file
file = open( config_file )
config_list = file.readlines()
file.close()

# populate dictionary
for i in config_list:
	string_key = process_string( i )
	if ( len( string_key ) > 0 ):
		config_strings[string_key] = 1

# open config doc file
file = open( py_release_file )
py_release_list = file.readlines()
file.close()

# populate dictionary
for i in py_release_list:
	string_key = process_string( i )
	if ( len( string_key ) > 0 ):
		py_release_strings[string_key] = 1

# check for missing
config_keys = config_strings.keys()
config_keys.sort()
for i in config_keys:
	if ( not py_release_strings.has_key( i ) ):
		print "Missing: "+i
print "----------------------------------"

# check for unused
py_release_keys = py_release_strings.keys()
py_release_keys.sort()
for i in py_release_keys:
	if ( not config_strings.has_key( i ) ):
		print "Unused: "+i
print "----------------------------------"
