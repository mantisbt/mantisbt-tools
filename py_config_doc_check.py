# /usr/bin/env python

# This file checkes the filename lengths of all files in a directory.
# Any files over 32 characters in length must be shortened.

import sys
from string import *
import os

# --- ------
# GOOD
def process_string( p_string ):
	p_string = translate( p_string, maketrans( "#()\\;<>:\".,", "           " ) )
	words = split( p_string )
	for a in words:
		if (( -1 != find( a, "$g_" ) )&
			( -1 == find( p_string, "$HTTP_COOKIE_VARS" ) )&
			( -1 == find( p_string, "_include_" ) )&
			( -1 == find( p_string, "_path" ) )):
			return a
	return ""
# --- ------

# ===========================
#             MAIN
# ===========================
config_file = "/home/www/mantis/config_inc.php"
config_doc_file = "/home/www/mantis/doc/configuration.html"
config_list = []
config_doc_list = []
config_strings = {}
config_doc_strings = {}

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
file = open( config_doc_file )
config_doc_list = file.readlines()
file.close()

# populate dictionary
for i in config_doc_list:
	string_key = process_string( i )
	if ( len( string_key ) > 0 ):
		config_doc_strings[string_key] = 1

# check for missing
config_keys = config_strings.keys()
config_keys.sort()
for i in config_keys:
	if ( not config_doc_strings.has_key( i ) ):
		print "Missing: "+i
print "----------------------------------"

# check for unused
config_doc_keys = config_doc_strings.keys()
config_doc_keys.sort()
for i in config_doc_keys:
	if ( not config_strings.has_key( i ) ):
		print "Unused: "+i
print "----------------------------------"