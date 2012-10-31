#!/bin/bash
#------------------------------------------------------------------------------
#
# nightly-builds.sh
#
# This script is intended to be scheduled for daily execution in cron, and
# will build the release tar/zipballs and make them available for download
# in the specified path.
#
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Parameters (edit variables as appropriate)
#

# List of branches to process
branches='master-1.2.x master'

# Where to save the builds
pathBuilds=/srv/www/builds

# Location of release build scripts
pathTools=$(dirname $(readlink -e $0))

# Log file - set to /dev/null for no log
logfile=/var/log/$(basename $0 .sh).log
#logfile=/dev/null


#------------------------------------------------------------------------------
# Main
#

today=`date +"%F %T"`

# Create target directory if it does not exist
if [ ! -d $pathBuilds ]
then
	mkdir -p $pathBuilds 2>&1 || exit 1
fi

for b in $branches
do
	echo "
------------------------------------------------------------------------
$today - Build release tarball for '$b' branch
"
	$pathTools/buildrelease-repo.py --auto-suffix --ref origin/$b --fresh --docbook $pathBuilds 2>&1
	echo
done >>$logfile

echo "Deleting old builds" >>$logfile
find $pathBuilds -mtime +1 -print -delete >>$logfile
