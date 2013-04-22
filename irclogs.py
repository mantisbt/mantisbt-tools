#!/usr/bin/env python2

# Processes the Supybot ChannelLogger's log directory and generates
# html pages for the IRC logs
# Assumes that the dir / log file names do not have a leading '#'

import re
import os
import glob
from os import path
from datetime import date

# ---------------------------------------------------------------------

# Directory where ChannelLogger stores the raw IRC logs
pathSource = '/tmp/irclogs/source'

# Web server directory from which the html pages are served
pathTarget = '/tmp/irclogs/target'

# Regex for IRC logs archives to process
strRegexChannel = '(?:mantis)'

# ---------------------------------------------------------------------

def runLogs2html (dirName):
    """ Calls Log2html script for specified directory """
    cmd = "logs2html %s" % dirName
    print "\tCalling", cmd
    os.system(cmd)


def convertLogs (pathSource):
    """ Process source path, convert all logs to html """

    # The directories in pathSource are our logged channels
    for channel in os.walk(pathSource).next()[1]:
        pathSrcChan = path.join(pathSource, channel)

        # Skip if channel not matching spec
        regexChannel = re.compile(strRegexChannel)
        if not regexChannel.match(channel):
            continue

        print "Processing channel #%s " % channel

        # Check for presence of subdirectories
        dirList = os.walk(pathSrcChan).next()[1]
        if dirList:
            # Found some (directories.timestamp is True), process them
            for d in dirList:
                dPath = path.join(pathSrcChan, d)
                fileMostRecent = max(glob.glob(path.join(dPath, '*.log')))
                print path.join(dPath, fileMostRecent + '.html')
                if os.path.exists(path.join(dPath, fileMostRecent + '.html')):
                    print "html exists"
                print fileMostRecent

#                runLogs2html(dPath)
        else:
            # Empty dirList = no dir rotation setup, all files are here
            runLogs2html(pathSrcChan)

        print


def updateWww (pathSource, pathTarget):
    """ Copies the generated html pages to the web server """
    rsync = "rsync -av --exclude=*.log %s/ %s" % (pathSource, pathTarget)
    print "Running rsync"
    print
    os.system(rsync)


# ---------------------------------------------------------------------

convertLogs(pathSource)
updateWww(pathSource, pathTarget)
