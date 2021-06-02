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
# Use '*' as wildcard to match branch names, e.g. master*, *1.3*
branches="master*"

# Path to reference MantisBT repository
# This is used to build the branches list when not specified
pathRepo=/srv/mantisbt

# Where to save the builds
pathBuilds=/srv/www/builds

# Number of nightly builds to keep available for download
numToKeep=2

# Location of release build scripts
pathTools=/srv/mantisbt/build

# Log file - set to /dev/null for no log
logfile=/var/log/$(basename "$0" .sh).log
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
# Functions
#

function log()
{
    DATE=$(date +"%F %T")
    echo "$@"
    echo "$DATE  $*" >>"$logfile"
}


#------------------------------------------------------------------------------
# Main
#

# Create target directory if it does not exist
if [ ! -d $pathBuilds ]
then
	mkdir -p $pathBuilds 2>&1 || exit 1
fi

# Start logging
cat <<-EOF >>"$logfile"

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
		log "phpenv: setting PHP version to '$PHPENV_phpVersion'"
		phpenv global "$PHPENV_phpVersion" 2>&1 >/dev/null |tee -a "$logfile"

		# Make sure the version was actually set
		if [ "$(set -- "$(phpenv version)"; echo "$1")" != "$PHPENV_phpVersion" ]
		then
			exit 1;
		fi
	else
		unset PHPENV_oldVersion
	fi
fi

# No branches or wildcard specified, get the list from the reference repo
if [[ -z "$branches" || "$branches" =~ \* ]]
then
	log "Retrieving branches from MantisBT repo in $pathRepo"

	if ! cd $pathRepo
	then
		echo "ERROR: invalid directory $pathRepo" >>"$logfile"
		exit 1
	fi

	tempfile=$(mktemp)
	# Make sure the origin remote exists
	if git remote show origin -n 2>"$tempfile" >/dev/null
	then
		if [[ "$branches" =~ ',' ]]
		then
			# Branches list contains multiple entries
			refList=$(eval echo "refs/heads/{$branches}")
		elif [[ -n "$branches" ]]
		then
			refList="refs/heads/$branches"
		else
			refList=""
		fi
		branches=$(git ls-remote --heads origin "$refList" | cut -d/ -f3- | paste -d, --serial)
	else
		cat "$tempfile" |tee -a "$logfile"
	fi
	rm "$tempfile"
	[[ -z "$branches" ]] && exit 1
fi

# Remove any builds not part of the branches list
log "Deleting old builds not part of branches list"
find $pathBuilds -maxdepth 1 -name 'mantisbt*' |
	grep -vE -- "-(${branches//,/|})-[0-9a-f]{7}" |
	xargs --no-run-if-empty rm -r 2>&1 |tee -a "$logfile"

# Build the tarballs
log "Generating nightly builds for branches: $branches"
refList=$(eval echo "origin/{$branches}")
if [[ $branches == *,* ]]
then
	refList=$(eval echo "origin/{$branches}")
else
	refList=origin/$branches
fi
$pathTools/buildrelease-repo.py --auto-suffix --ref "${refList// /,}" --fresh --clean $pathBuilds 2>&1 |tee -a "$logfile"
echo >>"$logfile"


# Delete old nightly builds
echo "Keeping only the most recent $numToKeep builds" |tee -a "$logfile"
# shellcheck disable=SC2164
cd $pathBuilds
for branch in ${branches//,/ }
do
	echo "  Processing '$branch' branch"
	# List files by date, grep for branch with shortened MD5 pattern and key
	# extension, and use tail to keep desired number
	# shellcheck disable=SC2004,SC2010
	ls -t | grep -P "$branch-[0-9a-f]+$keyExt$" | tail -n +$(($numToKeep + 1)) |
	while read -r build
	do
		fileSpec=$(basename "$build" $keyExt)
		echo "    Deleting files for $fileSpec"
		# shellcheck disable=SC2086
		rm -r $fileSpec*
	done
done |tee -a "$logfile"
echo >>"$logfile"


# Restore phpenv if necessary
if [ -n "$PHPENV_oldVersion" ]
then
	log "phpenv: restoring PHP version"
	phpenv global "$PHPENV_phpVersion"
fi

# All done !
log "Build complete !"
echo "Review logfile in $logfile"
