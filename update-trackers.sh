#!/bin/bash
#------------------------------------------------------------------------------
#
# update-trackers.sh
#
# Updates the reference branch in the bug trackers specified on command-line
# to the latest (or specified) commit (i.e. pull from upstream), then rebases
# the branch bearing the same name as the repo on top of the target commit (by
# default the HEAD of the reference branch).
#
# The assumption here is that the tracker is a git repository with 2 local
# branches
#  - reference branch, named like and tracking the upstream one
#  - tracker's customizations branch, having the same name as the repository
#
# Command-line Options
# -b Reference branch (see below for default value)
# -c Target commit (default to reference branch's head)
#
# Parameters
# $1..n	One or more paths to a git repo
#
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Default Parameters (edit variables as appropriate)
#

# The upstream reference branch to update in the target repository
UPDATE_BRANCH=master


#------------------------------------------------------------------------------
# Functions
#

function usage() {
	cat <<-EOF
		Syntax: $(basename $0) [-b Branch] [-c Commit] repo [...]

		Branch	Reference branch (defaults to '$UPDATE_BRANCH')
		Commit	Target commit to rebase tracker's branch to
		repo	Path to one or more target bugtrackers (git repositories)
	EOF
}


function process_error() {
	echo -ne "\nERROR: "
	if [ -n "$1" ]
	then
		echo $1
	fi

	if [ -n "$REPO" ]
	then
		echo "Fix issues in repository '$REPO' and try again"
	fi
	exit 1
}


#------------------------------------------------------------------------------
# Initialization
#

CONFIG_FILE=config/config_inc.php

# Parse command-line options
while getopts b:c:h OPT
do
    case $OPT in
        b)	# Reference branch
            UPDATE_BRANCH="$OPTARG"
            ;;

        c)	# Target commit
            TARGET_REF="$OPTARG"
            ;;

        h|?)
            usage
			exit
            ;;
    esac
done

# If no target commit specified, use upstream branch's HEAD
test -z "$TARGET_REF" &&
	TARGET_REF=$UPDATE_BRANCH

# Remaining arguments should be the list of trackers to process
shift $((${OPTIND}-1))
if [ -z "$1" ]
then
	usage
	echo
	process_error "Please specify the repository to process"
fi


#==============================================================================
# Main
#

for REPO in $*
do
	echo -e "Processing target repository: $REPO\n"

	DIR_NAME=$(dirname $REPO)
	if [[ -z "$DIR_NAME" || $DIR_NAME == "." ]]
	then
		DIR_NAME=$PWD
	fi
	REPO=$(basename $REPO)

	cd $DIR_NAME/$REPO 2>/dev/null ||
		process_error "repository '$REPO' does not exist in '$DIR_NAME' or is not accessible"

	# Detect if there are unstaged changes in the repository's current branch
	git diff-index --name-status --exit-code HEAD
	if [ $? -ne 0 ]
	then
		echo -e "\nThere are unstaged changes"
		read -n 1 -p "Would you like to discard them ? "
		echo
		if [ "$(echo ${REPLY} | tr "[:upper:]" "[:lower:]")" = "y" ]
		then
			echo "Discarding changes"
			git checkout -- . || process_error
		else
			process_error "can't proceed with unstaged changes"
		fi
	fi

	# First update the reference branch, pull changes from upstream
	echo "- Pulling upstream changes into reference branch '$UPDATE_BRANCH'"
	git checkout $UPDATE_BRANCH ||
		process_error "Unable to checkout branch '$UPDATE_BRANCH' !"
	git pull --ff-only ||
		process_error "failed to fast-forward branch '$UPDATE_BRANCH'"

	# Set the version suffix as 'RefBranch-CommitSHA'
	# If we're on a release tag, then the suffix is blank
	unset VERSION_SUFFIX
	git describe $TARGET_REF --exact-match >/dev/null 2>&1 ||
		VERSION_SUFFIX=-$UPDATE_BRANCH-$(git rev-parse --short $TARGET_REF)

	# If the repository-specific branch exists, we rebase it on the top of the
	# reference branch
	git checkout $REPO 2>/dev/null
	if [ $? -eq 0 ]
	then
		echo "- Rebasing local branch '$REPO' to '$TARGET_REF'"
		git rebase $TARGET_REF ||
			process_error "failed to rebase '$REPO' branch to '$TARGET_REF'"
	else
		echo "- WARNING: Unable to checkout local branch '$REPO'"
		continue
	fi

	# Update Composer packages
	echo "- Installing / Updating composer packages"
	composer install --no-plugins --no-scripts

	# Updating the version suffix in config file
	echo "- Setting version_suffix to '$VERSION_SUFFIX' in $CONFIG_FILE"
	test -f $CONFIG_FILE || process_error "missing $CONFIG_FILE"
	grep "^\s*\$g_version_suffix" $CONFIG_FILE >/dev/null
	if [ $? -eq 0 ]
	then
		echo "Updating existing config file"
		sed -r -i.bak "s/^(\s*\\\$g_version_suffix\s*=\s*[\"']).*([\"'])/\1$VERSION_SUFFIX\2/" $CONFIG_FILE
	else
		echo "Config option does not exist, appending it to end of file"
		echo "\$g_version_suffix = '$VERSION_SUFFIX';" >>$CONFIG_FILE
	fi

	# Syntax check the modified config file, just in case
	php -l $CONFIG_FILE ||
		process_error "Invalid $CONFIG_FILE"

	# Cleanup
	echo
	read -n 1 -p "The 'admin' directory should be deleted. Would you like to do it now ? "
	echo
	ADMIN_DIR=$PWD/admin
	if [ "$(echo ${REPLY} | tr "[:upper:]" "[:lower:]")" = "y" ]
	then
		rm -rvf $ADMIN_DIR
	else
		echo "WARNING: Remember to delete it after completing the upgrade (rm -rf $ADMIN_DIR)"
	fi

	echo -e "\nRepository '$REPO' updated successfully\n"
	cd - >/dev/null
done
