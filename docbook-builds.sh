#!/bin/bash
#-----------------------------------------------------------------------------
#
# MantisBT manuals build
#
# This script is intended to be scheduled with cron, and will build the
# MantisBT manual.
#
#-----------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Parameters (edit variables as appropriate)
#

# Log file - set to /dev/null for no log
LOGFILE=/var/log/$(basename "$0" .sh).log
#LOGFILE=/dev/null

# MantisBT repository, used to retrieve the build script (since 2.25.0)
# and to checkout the reference to build
# To avoid cluttering the log with unnecessary output, configure the repo
# with `git config advice.detachedHead false`
pathRepo=/srv/mantisbt

# Target directory for manuals
pathDocs=/srv/www/docs

# References to process
# Comma-delimited list of branches, prefixed by remote (e.g. origin/master)
refs=origin/master

# Languages to build (blank = all)
lang=


#------------------------------------------------------------------------------
# Functions
#

function log()
{
    DATE=$(date +"%F %T")
    echo "$@"
    echo "$DATE  $*" >>"$LOGFILE"
}


#------------------------------------------------------------------------------
# Main
#

log "Building MantisBT manuals"

cd "$pathRepo" >> "$LOGFILE" || exit 1

# Update reference repository
log "Updating repository in '$pathRepo'"
git checkout --force master |tee -a "$LOGFILE"
git pull --rebase |tee -a "$LOGFILE"

# Force build
if [[ "$1" = "-f" ]] || [[ "$1" = "--force" ]]
then
    force="--force"
fi

build/docbook-manual-repo.py --all $force --ref=$refs "$pathRepo" "$pathDocs" "$lang" 2>&1 |tee -a "$LOGFILE"

log "Build complete"
echo "--------------------------------------------" >>"$LOGFILE"
