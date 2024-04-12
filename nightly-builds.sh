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

# Space-delimited list of branches to process
# If blank, all branches present in the specified remote will be processed
# Use '*' as wildcard to match branch names, e.g. "master *2.*"
branches="master master-2*"

# Path to reference MantisBT repository and name of remote to use
# This is used to build the actual branches list from the above specification
pathRepo=/srv/mantisbt
remote=origin

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

function err()
{
	log "$*"
	exit 1
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

# Get the list of branches to build from the reference repo
if [[ "$branches" == '*' ]]
then
	branches=""
fi
# Disable globbing to ensure we display the '*' when $branches is empty
set -f
log "Retrieving branches matching '${branches:-*}'"
set +f

log "Switching to MantisBT repo in '$pathRepo'"
cd "$pathRepo" 2>>"$logfile" || err "ERROR: invalid repo directory '$pathRepo'"

set -o pipefail
# shellcheck disable=SC2086
expanded_branches=$(git ls-remote --heads $remote $branches | cut -d/ -f3- | paste -d, --serial)
[[ $? == 128 ]] &&
	err "ERROR: remote $remote not found"
set +o pipefail
[[ -z $expanded_branches ]] &&
	err "ERROR: no branches matching '$branches' found in repo"
log "Branches found: $expanded_branches"


# Remove any builds not part of the branches list
log "Deleting old builds not part of branches list"
find $pathBuilds -maxdepth 1 -name 'mantisbt*' -regextype egrep \
	! -regex ".*-(${expanded_branches//,/|})-[0-9a-f]{7,}\..*" -print0 |
	xargs -0 --no-run-if-empty rm -rv 2>&1 |tee -a "$logfile"

# Build the tarballs
log "Generating nightly builds for branches: $expanded_branches"
# Prefixing each branch name with remote
refList=$(eval echo "$remote/{$expanded_branches}")
echo $pathTools/buildrelease-repo.py --auto-suffix --ref "${refList// /,}" --fresh --clean $pathBuilds 2>&1 |tee -a "$logfile"
echo >>"$logfile"


# Delete old nightly builds
echo "Keeping only the most recent $numToKeep builds" |tee -a "$logfile"
# shellcheck disable=SC2164
cd $pathBuilds
for branch in ${expanded_branches//,/ }
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
		rm -rv $fileSpec* >> "$logfile"
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
