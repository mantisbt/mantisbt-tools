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

# Comma-delimited list of branches to process
branches='master-1.2.x,master'

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

# Create target directory if it does not exist
if [ ! -d $pathBuilds ]
then
	mkdir -p $pathBuilds 2>&1 || exit 1
fi

# Start logging
cat <<-EOF >>$logfile

	------------------------------------------------------------------------
	$(date +"%F %T") - Building release tarballs

EOF

# Build the tarballs
refList=$(eval echo origin/{$branches})
$pathTools/buildrelease-repo.py --auto-suffix --ref ${refList/ /,} --fresh --docbook $pathBuilds >>$logfile 2>&1
echo >>$logfile

echo "Deleting old builds" >>$logfile
find $pathBuilds -mtime +1 -print -delete >>$logfile
