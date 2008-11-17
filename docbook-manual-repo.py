#!/usr/bin/env python

# Integrates with docbook-manual.py to build manuals for all tagged
# versions and development branches in the Git repo

import os, sys
from os import path

import re

# Absolute path to docbook-manual.py
manualscript = path.dirname(path.abspath(__file__)) + '/docbook-manual.py'

# Regular expressions of refs to ignore
ignorelist = map(re.compile, [
			'HEAD',
			'-1\.0\.[\w\d]+',
			'-1\.1\.[\w\d]+'
			])

def usage():
	print '''Usage: docbook-manual-repo /path/to/mantisbt/repo /path/to/install [<lang> ...]'''

def ignore( ref ):
	'''Decide which refs to ignore based on regexen listed in 'ignorelist'.
	'''

	ignore = False
	for regex in ignorelist:
		if len(regex.findall(ref)) > 0:
			ignore = True
	return ignore
#end ignore()

def main():
	if len(sys.argv) < 3:
		usage()
		sys.exit(1)

	repo = sys.argv[1]
	installroot = sys.argv[2]
	languages = []

	if len(sys.argv) > 3:
		languages = sys.argv[3:]

	# Update repo from default remote
	os.chdir(repo)
	os.system('git fetch')

	# List refs from remote branches and tags
	branches = os.popen('git branch -r').read().split()
	tags = os.popen('git tag -l').read().split()

	# Filter refs using ignore()
	refs = [ref for ref in branches + tags if not ignore(ref)]

	# Regex to strip 'origin/' from ref names
	refnameregex = re.compile('(?:origin/)?(.*)')
	
	# For each ref, checkout and call docbook-manual.py, tracking last build timestamp
	# to prevent building a manual if there have been no commits since last build
	for ref in refs:
		manualpath = installroot.rstrip('/') + '/' + refnameregex.search( ref ).group(1)

		os.system('git checkout -f %s'%(ref))
		lastchange = os.popen('git log --pretty="format:%ct" -n1').read()

		buildfile = path.join(manualpath, '.build')
		lastbuild = 0
		if path.exists(buildfile):
			f = open(buildfile, 'r')
			lastbuild = f.read()
			f.close()

		if lastchange > lastbuild:
			buildcommand = '%s %s %s %s'%(manualscript, path.abspath('docbook'), manualpath, ' '.join(languages))
			if(os.system(buildcommand)):
				print 'here'

			f = open(buildfile, 'w')
			f.write(lastchange)
			f.close()
#end main

if __name__ == '__main__':
	main()
