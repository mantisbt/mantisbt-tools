#!/usr/bin/env python

import os, sys
from os import path

import getopt

# Script options
options = "hda"
long_options = [ "help", "delete", "all", "pdf", "html", "release" ]

def usage():
	print '''Usage: docbook-manual /path/to/mantisbt/docbook /path/to/install [<lang> ...]
    Options:  -h | --help           Print this usage message
	          -d | --delete         Delete install directory before building
                   --html           Build HTML manual
                   --pdf            Build PDF manual
                   --release        Build single file types used for release tarballs
              -a | --all            Build all manual types'''
#end usage()

def main():
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], options, long_options)
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	delete = False
	types = "html pdf"

	for opt, val in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit(0)

		elif opt in ("-d", "--delete"):
			delete = True

		elif opt in ("-a", "--all"):
			types = "html html_onefile html.tar.gz text pdf ps"

		elif opt == "--html":
			types = "html html_onefile html.tar.gz"

		elif opt == "--pdf":
			types = "pdf"

		elif opt == "--release":
			types = "html_onefile pdf text"

	if len(args) < 2:
		usage()
		sys.exit(1)

	docroot = args[0]
	installroot = args[1]
	languages = []

	if len(sys.argv) > 2:
		languages = args[2:]

	os.chdir( docroot )

	if delete and installroot != "/" and path.isdir( installroot ):
		print "Deleting install directory " + installroot
		for root, dirs, files in os.walk( installroot, topdown=False ):
			for name in files:
				os.remove( path.join( root, name ) )
			for name in dirs:
				os.rmdir( path.join( root, name ) )

	for dir in os.listdir( docroot ):
		if dir == '.svn' or dir == 'template':
			continue

		if len(languages) > 0:
			langs = languages
		else:
			langs = os.listdir( path.join( docroot, dir ) )
			if langs.count('.svn'):
				langs.remove('.svn')

		for lang in langs:
			builddir = path.join( docroot, dir, lang )
			installdir = path.join( installroot, lang ) 

			if path.isdir( builddir ):
				print "Building manual in " + builddir
				os.chdir( builddir )
				os.system( 'make clean %s 2>&1 && make INSTALL_DIR=%s install 2>&1'%(types, installdir) )
				os.system( 'make clean 2>&1' )
#end main

if __name__ == '__main__':
	main()
