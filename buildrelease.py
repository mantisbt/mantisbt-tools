#!/usr/bin/python -u

import getopt
import os
from os import path
import re
import sys
import tempfile

# Script options
options = "hcdv:s:"
long_options = ["help", "clean", "docbook", "version=", "suffix="]

# Absolute path to docbook-manual.py
manualscript = path.dirname(path.abspath(__file__)) + '/docbook-manual.py'

# List of files and dirs to exclude from the release tarball
exclude_list = (
    # System / build files
    ".git*",
    ".mailmap",
    ".travis.yml",
    "build.xml",
    "web.config",
    # User custom files
    "config_inc.php",
    "custom_constant*_inc.php",
    "custom_functions_inc.php",
    "custom_strings_inc.php",
    "custom_relationships_inc.php",
    "mantis_offline.php",
    "mc_config_inc.php",
    # Directories
    "docbook/",
    "javascript/dev/",
    "packages/",
    "phing/",
    "tests/"
    )


def usage():
    print '''Builds a release (zip/tarball)

Usage: %s [options] /path/for/tarballs [/path/to/mantisbt]

Options:
    -h | --help               Show this usage message

    -c | --clean              Remove build directory when completed
    -d | --docbook            Build and include the docbook manuals
    -v | --version <version>  Override version name detection
    -s | --suffix <suffix>    Include version suffix in config file
''' % path.basename(__file__)
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

    # 'Standard' umask
    old_umask = os.umask(0002)

    # Check paths
    if not path.isdir(release_path):
        print "Creating release path..."
        os.mkdir(release_path)

    if not path.isdir(mantis_path):
        print "Error: mantis path is not a directory or does not exist."
        sys.exit(3)

    if (
        not path.isfile(path.join(mantis_path, "core.php")) or
        not path.isdir(path.join(mantis_path, "core")) or
        not path.isfile(path.join(mantis_path, "core", "constant_inc.php"))
    ):
        print "Error: '%s' does not appear to be a valid Mantis directory." % \
            mantis_path
        sys.exit(3)

    # Find Mantis version
    if not mantis_version:
        f = open(path.join(mantis_path, "core", "constant_inc.php"))
        content = f.read()
        f.close

        mantis_version = re.search("'MANTIS_VERSION'[,\s]+'([^']+)'",
                                   content).group(1)

    # Generate release name
    release_name = 'mantisbt-' + mantis_version
    if version_suffix:
        release_name += '-' + version_suffix

    # Copy to release path, excluding unwanted files
    release_dir = path.join(release_path, release_name)

    print "\nBuilding release '%s' in path '%s'" % (release_name, release_dir)
    print "  Source repository: '%s'\n" % mantis_path

    if path.exists(release_dir):
        print "Error: release path already contains %s." % (release_name)
        sys.exit(3)

    # Generate temp file with list of exclusions
    fp = tempfile.NamedTemporaryFile(delete=False)
    print "  Excluded files and directories:"
    for name in exclude_list:
        print "    " + name
        fp.write(name + "\n")
    fp.close()

    # Copy the files from the source repo, then delete temp file
    os.system("rsync -rltD --exclude-from=%s %s/ %s" % (
        fp.name,
        mantis_path,
        release_dir
    ))
    os.unlink(fp.name)
    print "  Copy complete.\n"

    # Apply version suffix
    if version_suffix:
        print "Applying version suffix..."
        sed_cmd = "s,{0}(\s+)=(\s*)'.*',{0}\\1=\\2'{1}'".format(
            'g_version_suffix',
            version_suffix
        )
        os.system('sed -r -i.bak "%s", %s' % (
            sed_cmd,
            path.join(release_dir, "config_defaults_inc.php")
        ))

    # Build documentation for release
    if build_docbook:
        print "Building docbook manuals...\n"
        os.system("%s --release %s %s" % (
            manualscript,
            path.join(mantis_path, "docbook"),
            path.join(release_dir, "doc")
        ))

    # Create tarballs
    print "Creating release tarballs..."
    os.chdir(release_path)
    tarball_ext = ("tar.gz", "zip")

    for ext in tarball_ext:
        if ext == "tar.gz":
            tar_cmd = "tar czf"
        elif ext == "zip":
            tar_cmd = "zip -rq"
        tar_cmd += " %(rel)s.%(ext)s %(rel)s"

        print "  " + ext
        os.system(tar_cmd % {"rel": release_name, "ext": ext})

    # Sign tarballs
    print "Signing tarballs"

    os.system("gpg -b -a %s.tar.gz" % (release_name))
    os.system("gpg -b -a %s.zip" % (release_name))

    # Generate checksums
    print "Generating checksums..."

    tar_md5 = os.popen("md5sum --binary %s.tar.gz" % (release_name)).read()
    tar_sha1 = os.popen("sha1sum --binary %s.tar.gz" % (release_name)).read()

    zip_md5 = os.popen("md5sum --binary %s.zip" % (release_name)).read()
    zip_sha1 = os.popen("sha1sum --binary %s.zip" % (release_name)).read()

    f = open("%s.tar.gz.digests" % release_name, 'w')
    f.write("%s\n%s\n" % (tar_md5, tar_sha1))
    f.close()

    f = open("%s.zip.digests" % release_name, 'w')
    f.write("%s\n%s\n" % (zip_md5, zip_sha1))
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

    # Restore previous umask
    os.umask(old_umask)

    print "Done!\n"

#end main()

if __name__ == "__main__":
    main()
