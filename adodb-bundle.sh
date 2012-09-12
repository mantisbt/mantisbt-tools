#!/bin/bash

#
# This script will prepare the ADOdb library, as extracted from the upstream
# release tarball, to be bundled with MantisBT.
#
# The following operations are performed:
#  - Removing unnecessary dirs and files (see TO_DELETE below for full list)
#  - Converting line endings to Unix format (CRLF ==> CR)
#  - Removing trailing whitespace
#

# -----------------------------------------------------------------------------
# Init
#

# Space-delimited list of dirs and files to delete
# (i.e. not to be bundled with MantisBT)
TO_DELETE="contrib/ cute_icons_for_site/ docs/ pear/ tests/ server.php"

if [ -d "$1" ]
then
	cd $1
elif [ -n "$1" ]
then
	echo "ERROR: Specified directory '$1' does not exist"
	exit 1
fi

if [ ! -f "adodb.inc.php" ]
then
	echo "ERROR: directory '$PWD' does not seem to contain the ADOdb library"
	exit 1
fi

# -----------------------------------------------------------------------------
# Main
#

echo "Removing files and directories not to be bundled with MantisBT"
echo $TO_DELETE
rm -r $TO_DELETE
echo

echo "Converting line endings to Unix format"
find . -type f ! -path "./.git*" -print0 |xargs -0 dos2unix
echo

echo "Removing trailing whitespace"
find . -type f ! -path "./.git*" -print0 |xargs -0 sed -i.bak -e 's/[ \t]*$//'

# Removing backup files if sed execution successful
if [ $? -eq 0 ]
then
	find . -name '*.bak' -delete
else
	echo "ERROR occured"
	exit 1
fi
echo

echo "Done!

Remember to edit the README.libs file as appropriate, after moving the updated
release in '$PWD' to the MantisBT ./library directory.
"
