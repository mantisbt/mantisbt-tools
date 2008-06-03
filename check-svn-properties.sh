#!/bin/sh

#
# check-svn-properties.sh
#
# This script sets the required Subversion properties for all files in
# the current directory and all subdirectories based on file extensions.
# As result the current difference to be checked in is written to stdout.
#

svn up

find . -name \*.php -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.php -exec svn propset svn:keywords 'Id' {} \; >/dev/null
find . -name \*.txt -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.txt -exec svn propset svn:keywords 'Id' {} \; >/dev/null
find . -name \*.sgml -exec svn propset svn:mime-type text/sgml {} \; >/dev/null
find . -name \*.sgml -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.sgml -exec svn propset svn:keywords 'Id' {} \; >/dev/null
find . -name \*.dsl -exec svn propset svn:mime-type text/xml {} \; >/dev/null
find . -name \*.dsl -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.ent -exec svn propset svn:mime-type text/xml {} \; >/dev/null
find . -name \*.ent -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.css -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.js -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.sample -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.htm -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.html -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name .htaccess -exec svn propset svn:eol-style native {} \; >/dev/null
find . -name \*.png -exec svn propset svn:mime-type image/png {} \; >/dev/null
find . -name \*.jpg -exec svn propset svn:mime-type image/jpeg {} \; >/dev/null
find . -name \*.gif -exec svn propset svn:mime-type image/gif {} \; >/dev/null

svn di
