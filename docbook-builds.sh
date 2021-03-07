#!/bin/bash
# MantisBT manuals build

LOGFILE=/var/log/$(basename $0).log

# references to build
refs=origin/master-1.3.x,origin/master

# MantisBT repository
repo=/srv/mantisbt

# Target directory for manuals
docs=/srv/www/docs

# Languages to build (blank = all)
lang=

# Force build
if [[ "$1" = "-f" ]] || [[ "$1" = "--force" ]]
then
        force="--force"
fi

echo $(date +"%F %T") '  Building MantisBT manuals' >>$LOGFILE
/srv/mantisbt-tools/docbook-manual-repo.py --all $force --ref=$refs $repo $docs $lang >>$LOGFILE 2>&1
echo $(date +"%F %T") '  Build complete' >>$LOGFILE
echo "--------------------------------------------" >>$LOGFILE
