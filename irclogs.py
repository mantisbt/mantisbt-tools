#!/usr/bin/python3 -u

# Processes the Supybot ChannelLogger's log directory and generates
# html pages for the IRC logs
# Assumes that the dir / log file names do not have a leading '#'

import datetime
import re
import os
import subprocess
import sys
import glob
from os import path

# ---------------------------------------------------------------------

# Directory where ChannelLogger stores the raw IRC logs
source = '/home/supybot/mantisbot/logs/ChannelLogger'

# Web server directory from which the html pages are served
target_dir = '/srv/www/irclogs'

# Regex for IRC logs archives to process
regexstr_channel = '(?:mantis)'

# ---------------------------------------------------------------------


def log(msg):
    """
    Prints log message with timestamp
    """
    print("%s  %s".format(
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        msg
    ))


def check_path(p):
    """
    Converts path to absolute and check that it exists
    """
    p = path.abspath(p)
    if not path.isdir(p):
        print("ERROR: %s is not a directory" % p)
        exit(1)
    return p


def run_logs2html(channel, dir_name):
    """
    Runs the Log2html script for specified directory if the most
    recent log file does not have a corresponding and up-to-date
    html file
    """

    # Get most recent log file
    path_recent_log = max(glob.glob(path.join(dir_name, '*.log')))
    path_recent_html = path_recent_log + '.html'

    # Check that html file corresponding to most recent log
    # exists and is actually more recent than the log file
    if (
            path.exists(path_recent_html) and
            path.getmtime(path_recent_log) <= path.getmtime(path_recent_html)):
        print("up-to-date html exists for newest log file %s" % (
            path.basename(path_recent_log)
        ))
    else:
        msg = "IRC logs of #%s" % channel
        cmd = "logs2html --title='%s' --prefix='%s for ' %s" % (
            msg, msg, dir_name
        )
        print("generating html - %s" % cmd)
        # Execute logs2html, redirect stderr to stdout for logging purposes
        subprocess.check_call(cmd, shell=True, stderr=sys.stdout.fileno())


def convert_logs(source):
    """
    Process source path, convert all logs to html
    """

    # Building a list of channels to generate index page later
    channels = dict()

    # The directories in source are our logged channels
    for channel in next(os.walk(source))[1]:
        path_src_channel = path.join(source, channel)
        channels[channel] = set()

        # Skip if channel not matching spec
        regex_channel = re.compile(regexstr_channel)
        if not regex_channel.match(channel):
            continue

        print("Processing channel #%s " % channel)

        # Check for presence of subdirectories
        dirlist = frozenset(next(os.walk(path_src_channel))[1])
        if dirlist:
            # Found some (directories.timestamp is True), process them
            for subdir in dirlist:
                channels[channel].add(subdir)
                print("\t%s:" % subdir, end=' ')
                run_logs2html(channel, path.join(path_src_channel, subdir))
        else:
            # Empty dirlist = no dir rotation setup, all files are here
            print("\t", end=' ')
            run_logs2html(channel, path_src_channel)

    print("html files generation completed")
    print()

    return channels


def www_update(source, target):
    """
    Copies the generated html pages to the web server
    """
    log("Copying HTML pages to '%s'" % target)
    rsync = "rsync -av --delete --exclude=*.log %s/ %s" % (
        source, target
    )
    print(rsync)
    print()
    exitcode = subprocess.call(rsync, shell=True)
    if exitcode != 0:
        log('ERROR: rsync call failed with exit code %i' % exitcode)


# ---------------------------------------------------------------------

log('Converting logfiles')

source_dir = check_path(source_dir)
target_dir = check_path(target_dir)

convert_logs(source_dir)
www_update(source_dir, target_dir)

log('Completed\n%s' % ('-' * 80))
