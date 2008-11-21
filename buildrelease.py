#!/usr/bin/env python

import os, sys
from os import path

import getopt
import re

# Script options
options = "hcdv:s:"
long_options = [ "help", "clean", "docbook", "version=", "suffix=" ]

# Absolute path to docbook-manual.py
manualscript = path.dirname(path.abspath(__file__)) + '/docbook-manual.py'

def usage():
	print '''Usage: buildrelease [options] /path/for/tarballs [/path/to/mantisbt]
Options:  -h | --help               Show this usage message
          -c | --clean              Remove build directory when completed
          -d | --docbook            Build the docbook manuals
          -v | --version <version>  Override version name detection
          -s | --suffix <suffix>    Include version suffix in config file'''
#end usage()

def main():
	try:
		opts, args = getopt.gnu_getopt(sys.argv[1:], options, long_options)
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	build_docbook = False
	clean_build = False
	mantis_version = ""
	version_suffix = ""

	for opt, val in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit(0)

		elif opt in ("-c", "--clean"):
			clean_build = True

		elif opt in ("-d", "--docbook"):
			build_docbook = True

		elif opt in ("-v", "--version"):
			mantis_version = val

		elif opt in ("-s", "--suffix"):
			version_suffix = val

	if len(args) < 1:
		usage()
		sys.exit(1)

	release_path = args[0]
	mantis_path = "."

	if len(args) > 1:
		mantis_path = args[1]

	# Check paths
	if not path.isdir(release_path):
		print "Creating release path..."
		os.mkdir(release_path)

	if not path.isdir(mantis_path):
		print "Error: mantis path is not a directory or does not exist."
		sys.exit(3)

	if not path.isfile(path.join(mantis_path, "core.php"))\
		or not path.isdir(path.join(mantis_path, "core"))\
		or not path.isfile(path.join(mantis_path, "core", "constant_inc.php")):

		print "Error: mantis path does not appear to be a valid Mantis directory."
		sys.exit(3)

	# Find Mantis version
	if not mantis_version:
		f = open(path.join(mantis_path, "core", "constant_inc.php"))
		content = f.read()
		f.close

		mantis_version = re.search("'MANTIS_VERSION'[,\s]+'([^']+)'", content).group(1)

	# Generate release name
	release_name = 'mantisbt-' + mantis_version

	if version_suffix:
		release_name += '-' + version_suffix

	# Copy to release path, removing custom files
	release_dir = path.join(release_path, release_name)

	print "Building release '%s' in path '%s'"%(release_name, release_dir)

	if path.exists(release_dir):
		print "Error: release path already contains %s."%(release_name)
		sys.exit(3)

	os.system("rsync -a --exclude=.git %s/ %s"%(mantis_path, release_dir))

	# Apply version suffix
	if version_suffix:
		print "Applying version suffix..."
		os.system("sed -r -i=bak \"s,g_version_suffix(\s+)=(\s*)'.*',g_version_suffix\\1=\\2'%s'\", %s"%(
			version_suffix, path.join(release_dir, "config_defaults_inc.php")))

	# Walk through and remove custom files
	print "Removing custom files from release path..."

	def custom_files(name):
		return True if name in (
				"config_inc.php",
				"custom_constant_inc.php",
				"custom_strings_inc.php",
				"custom_functions_inc.php",
				"mantis_offline.php",
				"web.config"
				) else False

	def custom_dirs(name):
		return True if name in (
				"packages"
				) else False

	for root, dirs, files in os.walk(release_dir, topdown=False):
		files = filter(custom_files, files)
		dirs = filter(custom_dirs, dirs)
		for name in files:
			print "  " + path.join(root,name)
			os.remove(path.join(root, name))
		for name in dirs:
			print "  " + path.join(root,name) + "/"
			os.system("rm -rf %s"%path.join(root, name))

	# Build documentation for release	
	if build_docbook:
		print "Building docbook manuals..."
		os.system("%s --release %s %s"%(manualscript, path.join(release_dir, "docbook"), path.join(release_dir, "doc")))

	# Create tarballs
	print "Creating release tarballs..."

	os.chdir(release_path)
	os.system("tar czf %s.tgz %s"%(release_name, release_name))
	os.system("zip -rq %s.zip %s"%(release_name, release_name))

	# Generate checksums
	print "Generating checksums..."

	tar_md5 = os.popen("md5sum --binary %s.tgz"%(release_name)).read()
	tar_sha1 = os.popen("sha1sum --binary %s.tgz"%(release_name)).read()

	zip_md5 = os.popen("md5sum --binary %s.zip"%(release_name)).read()
	zip_sha1 = os.popen("sha1sum --binary %s.zip"%(release_name)).read()

	f = open("%s.tgz.digests"%release_name, 'w')
	f.write("%s\n%s\n"%(tar_md5, tar_sha1))
	f.close()

	f = open("%s.zip.digests"%release_name, 'w')
	f.write("%s\n%s\n"%(zip_md5, zip_sha1))
	f.close()

	print "  " + tar_md5
	print "  " + tar_sha1
	print "  " + zip_md5
	print "  " + zip_sha1

	# Cleanup
	if clean_build:
		print "Removing build directory..."
		for root, dirs, files in os.walk(release_dir, topdown=False):
			for name in files:
				os.remove(path.join(root, name))
			for name in dirs:
				os.rmdir(path.join(root, name))
		os.rmdir(release_dir)
	
	print "Done!"

#end main()

if __name__ == "__main__":
	main()
