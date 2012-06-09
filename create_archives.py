#!/usr/bin/env python

import os, sys
from os import path

import getopt
import re

def usage():
    print '''Usage: package release-name

    This script expects that the release folder is in the current directory with the specified name.
    The output archives and checksums will be generated in the current directory.'''
#end usage()

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    release_name = sys.argv[1]
    mantis_path = './' + release_name
    print "Packing from ", mantis_path

    if not path.isfile(path.join(mantis_path, "core.php"))\
        or not path.isdir(path.join(mantis_path, "core"))\
        or not path.isfile(path.join(mantis_path, "core", "constant_inc.php")):

        print "Error: mantis path does not appear to be a valid Mantis directory."
        sys.exit(3)

    # Create tarballs
    print "Creating release tarballs..."

    os.system("tar czf %s.tar.gz %s"%(release_name, release_name))
    os.system("zip -rq %s.zip %s"%(release_name, release_name))

    # Sign tarballs
    print "Signing tarballs"

    os.system("gpg -b -a %s.tar.gz"%(release_name))
    os.system("gpg -b -a %s.zip"%(release_name))

    # Generate checksums
    print "Generating checksums..."

    tar_md5 = os.popen("md5sum --binary %s.tar.gz"%(release_name)).read()
    tar_sha1 = os.popen("sha1sum --binary %s.tar.gz"%(release_name)).read()

    zip_md5 = os.popen("md5sum --binary %s.zip"%(release_name)).read()
    zip_sha1 = os.popen("sha1sum --binary %s.zip"%(release_name)).read()

    f = open("%s.tar.gz.digests"%release_name, 'w')
    f.write("%s\n%s\n"%(tar_md5, tar_sha1))
    f.close()

    f = open("%s.zip.digests"%release_name, 'w')
    f.write("%s\n%s\n"%(zip_md5, zip_sha1))
    f.close()

    print "  " + tar_md5
    print "  " + tar_sha1
    print "  " + zip_md5
    print "  " + zip_sha1

    print "Done!"

#end main()

if __name__ == "__main__":
    main()
