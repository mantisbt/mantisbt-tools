# /usr/bin/env python

# This file checkes the filename lengths of all files in a directory.
# Any files over 32 characters in length must be shortened.

import sys
from string import *
import os

directory = ".";
if ( len(sys.argv) < 1 ):
	directory = sys.argv[1]

dirlist = os.listdir( directory )
file_count = len( dirlist )

print "Checking filename length (over 32 characters)."
print "Checking "+str( file_count )+" files:\n"
for a in dirlist:
    if ( len( a ) > 32 ):
        print a+"\n"

print "\nFinished checking files.\n"
