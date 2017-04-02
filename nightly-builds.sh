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
branches='master,master-2.0.x,master-1.3.x'

# Where to save the builds
pathBuilds=/srv/www/builds

# Number of nightly builds to keep available for download
numToKeep=2

# Location of release build scripts
pathTools=$(dirname $(readlink -e $0))

# Log file - set to /dev/null for no log
logfile=/var/log/$(basename $0 .sh).log
#logfile=/dev/null

# Key extension used to determine old releases to delete
keyExt='.zip'


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

# Remove any builds not part of the branches list
echo "$(date +'%F %T') Deleting old builds not part of branches list" |tee -a $logfile
find $pathBuilds -maxdepth 1 -name 'mantisbt*' |
	grep -vE -- "-(${branches//,/|})-[0-9a-f]{7}" |
	xargs --no-run-if-empty rm -r 2>&1 |tee -a $logfile

# Build the tarballs
echo "$(date +'%F %T') Generating nightly builds for branches:" |tee -a $logfile
refList=$(eval echo origin/{$branches})
if [[ $branches == *,* ]]
then
	refList=$(eval echo origin/{$branches})
else
	refList=origin/$branches
fi
$pathTools/buildrelease-repo.py --auto-suffix --ref ${refList// /,} --fresh --docbook $pathBuilds 2>&1 |tee -a $logfile
echo >>$logfile


# Delete old nightly builds
echo "Keeping only the most recent $numToKeep builds" |tee -a $logfile
cd $pathBuilds
for branch in ${branches//,/ }
do
	echo "  Processing '$branch' branch"
	# List files by date, grep for branch with shortened MD5 pattern and key
	# extension, and use tail to keep desired number
	ls -t | grep -P "$branch-[0-9a-f]{7}$keyExt$" | tail -n +$(($numToKeep + 1)) |
	while read build
	do
		fileSpec=$(basename $build $keyExt)
		echo "    Deleting files for $fileSpec"
		rm -r $fileSpec*
	done
done |tee -a $logfile
echo >>$logfile


# All done !
echo "$(date +'%F %T') Build complete !" |tee -a $logfile
echo "Review logfile in $logfile"
