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
# If blank, all branches present in the 'origin' remote will be processed
branches=

# Path to reference MantisBT repository
# This is used to build the branches list when not specified
pathRepo=/srv/mantisbt

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

# Directory in which phpenv is installed. The script will take care of
# initializing the environment (i.e. set PATH and run 'phpenv init')
export PHPENV_ROOT=/srv/phpenv

# PHP version to use for builds (set with phpenv)
# - version must be setup and compiled with 'phpenv install'
# - to use the system's PHP version (i.e. don't use phpenv), set to blank
PHPENV_phpVersion=

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

# Set PHP version to use for the builds
if [ -n "$PHPENV_phpVersion" ]
then
	# Initialize phpenv
	export PATH=$PHPENV_ROOT/bin:$PATH
	eval "$(phpenv init -)"
	PHPENV_oldVersion=$(phpenv global)

	if [ "$PHPENV_phpVersion" != "$PHPENV_oldVersion" ]
	then
		echo "$(date +'%F %T') phpenv: setting PHP version to '$PHPENV_phpVersion'" |tee -a $logfile
		phpenv global $PHPENV_phpVersion 2>&1 >/dev/null |tee -a $logfile

		# Make sure the version was actually set
		if [ "$(set -- $(phpenv version); echo $1)" != "$PHPENV_phpVersion" ]
		then
			exit 1;
		fi
	else
		unset PHPENV_oldVersion
	fi
fi

# No branches specified, get the list from the reference repo
if [[ -z "$branches" ]]
then
	echo "$(date +'%F %T') Retrieving branches from MantisBT repo in $pathRepo" |tee -a $logfile

	cd $pathRepo
	if [[ $? != 0 ]]
	then
		echo "ERROR: invalid directory $pathRepo" >>$logfile
		exit 1
	fi

	tempfile=$(mktemp)
	if git remote show origin -n 2>$tempfile >/dev/null
	then
		branches=$(git ls-remote --heads origin | cut -d/ -f3 | paste -d, --serial)
	else
		cat $tempfile |tee -a $logfile
	fi
	rm $tempfile
	[[ -z "$branches" ]] && exit 1
fi

# Remove any builds not part of the branches list
echo "$(date +'%F %T') Deleting old builds not part of branches list" |tee -a $logfile
find $pathBuilds -maxdepth 1 -name 'mantisbt*' |
	grep -vE -- "-(${branches//,/|})-[0-9a-f]{7}" |
	xargs --no-run-if-empty rm -r 2>&1 |tee -a $logfile

# Build the tarballs
echo "$(date +'%F %T') Generating nightly builds for branches: $branches" |tee -a $logfile
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


# Restore phpenv if necessary
if [ -n "$PHPENV_oldVersion" ]
then
	echo "$(date +'%F %T') phpenv: restoring PHP version" |tee -a $logfile
	phpenv global $PHPENV_phpVersion
fi

# All done !
echo "$(date +'%F %T') Build complete !" |tee -a $logfile
echo "Review logfile in $logfile"
