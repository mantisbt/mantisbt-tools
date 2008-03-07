#!/usr/bin/env python

import os, sys
from os import path

def usage():
	print '''Usage: docbook-manual /path/to/mantisbt/docbook /path/to/install [<lang> ...]'''

def main():
	if len(sys.argv) < 3:
		usage()
		sys.exit(1)

	svnroot = sys.argv[1]
	installroot = sys.argv[2]
	languages = []

	if len(sys.argv) > 3:
		languages = sys.argv[3:]

	print "Updating SVN checkout..."
	os.chdir( svnroot )
	os.system( 'svn update' )

	for dir in os.listdir( svnroot ):
		if dir == '.svn' or dir == 'template':
			continue

		if len(languages) > 0:
			langs = languages
		else:
			langs = os.listdir( path.join( svnroot, dir ) )
			if langs.count('.svn'):
				langs.remove('.svn')

		for lang in langs:
			builddir = path.join( svnroot, dir, lang )
			installdir = path.join( installroot, lang ) 
			if path.isdir( builddir ):
				print "Building manual in " + builddir
				os.chdir( builddir )
				os.system( 'make clean html 2>&1 && make INSTALL_DIR=' + installdir + ' install 2>&1' )
#end main

if __name__ == '__main__':
	main()