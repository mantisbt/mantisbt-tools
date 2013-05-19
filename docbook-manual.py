#!/usr/bin/env python

import os, sys
import errno
import glob
import shutil
import subprocess
from os import path

import getopt

# Constants
MAKE = 'make'
PUBLICAN = 'publican'

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

    if len(args) < 2:
        usage()
        sys.exit(1)

    delete = False
    types = {MAKE: "html pdf", PUBLICAN: "html,pdf"}

    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

        elif opt in ("-d", "--delete"):
            delete = True

        elif opt in ("-a", "--all"):
            types[MAKE] = "html html_onefile html.tar.gz text pdf ps"
            types[PUBLICAN] = "html,html-desktop,txt,pdf"

        elif opt == "--html":
            types[MAKE] = "html html_onefile html.tar.gz"
            types[PUBLICAN] = "html,html-desktop"

        elif opt == "--pdf":
            types[MAKE] = "pdf"
            types[PUBLICAN] = types[MAKE]

        elif opt == "--release":
            types[MAKE] = "html_onefile pdf text"
            types[PUBLICAN] = "html-desktop,pdf,txt"

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

    buildcount = 0

    # Process all existing manuals
    for dir in os.walk(docroot).next()[1]:
        if dir == '.svn' or dir == 'template':
            continue

        builddir = path.join( docroot, dir )
        os.chdir( builddir )

        # Languages to process
        if len(languages) > 0:
            langs = languages
        else:
            langs = os.walk(builddir).next()[1]
            if langs.count('.svn'):
                langs.remove('.svn')
            if langs.count('tmp'):
                langs.remove('tmp')

        if path.exists('publican.cfg'):
            # Build docbook with PUBLICAN

            print "Building manual in '%s'\n" % builddir
            os.system('publican clean')
            os.system('publican build --formats=%s --langs=%s' % (types[PUBLICAN], ','.join(langs)))

            print "\nCopying generated manuals to '%s'" % installroot
            for lang in langs:
                builddir = path.join('tmp', lang)
                installdir = path.join(installroot, lang, dir)

                # Create target directory tree
                try:
                    os.makedirs(installdir)
                except OSError as e:
                    # Ignore file exists error
                    if e.errno != errno.EEXIST:
                        raise

                # Copy HTML manuals with rsync
                rsync = "rsync -a --delete %s %s" % (path.join(builddir, 'html*'), installdir)
                print rsync
                retCode = subprocess.call(rsync, shell=True)
                if retCode != 0:
                    log('ERROR: rsync call failed with exit code %i' % retCode)

                # Copy PDF and TXT files (if built)
                for filetype in ['pdf', 'txt']:
                    for f in glob.glob(path.join(builddir, filetype, '*')):
                        shutil.copy2(f, installdir)

            os.system('publican clean')
            print "\nBuild complete\n"
            buildcount += len(langs)
        else:
            # Build docbook with MAKE

            for lang in langs:
                if not path.isdir(path.join(builddir, lang)):
                    print "WARNING: Unknown language '%s' in '%s'" % (lang, builddir)
                    continue

                builddir = path.join( builddir, lang )
                installdir = path.join( installroot, lang )
                os.chdir( builddir )

                if not path.exists('Makefile'):
                    continue

                print "Building manual in '%s'\n" % builddir
                os.system( 'make clean %s 2>&1 && make INSTALL_DIR=%s install 2>&1'%(types[MAKE], installdir) )
                os.system( 'make clean 2>&1' )
                print "\nBuild complete\n"
                buildcount += 1

    # end docbook build loop

    print "Done - %s docbooks built.\n" % buildcount


#end main

if __name__ == '__main__':
    main()
