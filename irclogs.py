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
pathSource = '/home/supybot/mantisbot/logs/ChannelLogger'

# Web server directory from which the html pages are served
pathTarget = '/srv/www/irclogs'

# Regex for IRC logs archives to process
strRegexChannel = '(?:mantis)'

# ---------------------------------------------------------------------

def checkPath (p):
    """ Converts path to absolute and check that it exists """
    p = os.path.abspath(p)
    if not path.isdir(p):
        print "ERROR: %s is not a directory" % p
        exit(1)
    return p


def runLogs2html (channel, dirName):
    """ Runs the Log2html script for specified directory if the most
    recent log file does not have a corresponding and up-to-date
    html file"""

    # Get most recent log file
    pathRecentLog = max(glob.glob(path.join(dirName, '*.log')))
    pathRecentHtml = pathRecentLog + '.html'

    # Check that html file corresponding to most recent log
    # exists and is actually more recent than the log file
    if (
        os.path.exists(pathRecentHtml) and
        os.path.getmtime(pathRecentLog) <= os.path.getmtime(pathRecentHtml)
    ):
        print "up-to-date html exists for newest log file %s" % \
            path.basename(pathRecentLog)
    else:
        msg = "IRC logs of #%s" % channel
        cmd = "logs2html --title='%s' --prefix='%s for ' %s" % (msg, msg, dirName)
        print "generating html - %s" % cmd
        os.system(cmd)


def convertLogs (pathSource):
    """ Process source path, convert all logs to html """

    # Building a list of channels to generate index page later
    channels = dict()

    # The directories in pathSource are our logged channels
    for channel in os.walk(pathSource).next()[1]:
        pathSrcChan = path.join(pathSource, channel)
        channels[channel] = set()

        # Skip if channel not matching spec
        regexChannel = re.compile(strRegexChannel)
        if not regexChannel.match(channel):
            continue

        print "Processing channel #%s " % channel

        # Check for presence of subdirectories
        dirList = frozenset(os.walk(pathSrcChan).next()[1])
        if dirList:
            # Found some (directories.timestamp is True), process them
            for subdir in dirList:
                channels[channel].add(subdir)
                print "\t%s:" % subdir,
                runLogs2html(channel, path.join(pathSrcChan, subdir))
        else:
            # Empty dirList = no dir rotation setup, all files are here
            print "\t",
            runLogs2html(channel, pathSrcChan)

    print "html files generation completed"
    print

    return channels


def wwwUpdate (pathSource, pathTarget):
    """ Copies the generated html pages to the web server """
    rsync = "rsync -av --delete --exclude=*.log --exclude=index.php %s/ %s" % (pathSource, pathTarget)
    print "Running rsync"
    print
    os.system(rsync)
    print


# ---------------------------------------------------------------------

pathSource = checkPath(pathSource)
pathTarget = checkPath(pathTarget)

convertLogs(pathSource)
wwwUpdate(pathSource, pathTarget)
