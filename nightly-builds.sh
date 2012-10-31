#!/bin/bash

#pushd /srv/mantisbt-tools > /dev/null
#git pull --rebase > /dev/null 2>&1
#popd > /dev/null

today=`date +"%F %T"`

logfile=/dev/null

branches='master-1.2.x master'

for b in $branches
do
        echo '---------------------------------------------------------------' >>$logfile
        echo "$today - Build release tarball for '$b'" >>$logfile
        /srv/mantisbt-tools/buildrelease-repo.py --auto-suffix --ref origin/$b --fresh --docbook /srv/www/builds >>$logfile 2>&1
done

echo "Deleting old builds" >>$logfile
find /srv/www/builds -mtime +1 -delete -print >>$logfile
