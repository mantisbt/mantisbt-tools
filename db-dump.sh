#!/bin/bash -e
#------------------------------------------------------------------------------
#
# db-dump.sh
#
# Creates a clone of the specified mantis database, runs some SQL to cleanup/
# anonymize the data, and dumps the clone in compressed format in the target
# directory.
#
# The script assumes that the user running the script has configured the MySQL
# client to connect without having to provide a password, and has sufficient
# privileges to read the reference DB and create a clone
#
# Parameters
# $1 name of database to dump (defaults to 'bugtracker')
# $2 directory to save the dump file (defaults to '/tmp')
#
#------------------------------------------------------------------------------

# Defaults
DBNAME=bugtracker
TARGETDIR=/tmp

#------------------------------------------------------------------------------
# Parameters
#

# Source database name
if [[ -n "$1" ]]
then
	if [[ "$1" == "-h" ]]
	then
		exit 0
		cat <<-EOF
			Syntax: $(basename $0) [Database [Directory]]

			Dumps the specified MantisBT database after anonymizing sensitive data.

			Database	Name of database to dump (defaults to 'bugtracker')
			Directory	Directory to save the dump file (defaults to '/tmp')

		EOF
	fi
	DBNAME=$1
fi

# Target Directory
if [[ -n "$2" ]]
then
	TARGETDIR=$2
fi
if [[ ! -d "$TARGETDIR" ]]
then
	echo "ERROR: Specified target '$TARGETDIR' is not a directory"
	exit 1
fi

# Target dump file name
DUMPFILE=$TARGETDIR/${DBNAME}_dump_$(date +"%Y%m%d").sql.bz2

#------------------------------------------------------------------------------
# Initialization
#

# Temporary database clone
DBCLONE=${DBNAME}_clone_$RANDOM

# DB anonymization script
SQL_ANONYMIZE=$(dirname $0)/db-anonymize.sql

# Trap signals to ensure we drop the temporary clone database in case of
# unexpected interuption
trap "{
	echo \"Dropping temporary database '$DBCLONE'\"
	mysql -e \"DROP DATABASE $DBCLONE\"
}" EXIT


#------------------------------------------------------------------------------
# Start cloning
#

echo "Cloning '$DBNAME' to '$DBCLONE'"
mysql -e "CREATE DATABASE $DBCLONE"
set -o pipefail
mysqldump --lock-tables $DBNAME |mysql $DBCLONE

echo "Clean up and anonymize the cloned database"
mysql -v $DBCLONE <$SQL_ANONYMIZE

echo "Dumping '$DBCLONE' to '$TARGETDIR'"
mysqldump $DBNAME | bzip2 > $DUMPFILE

echo "Dump saved in '$DUMPFILE'"

# Temporary clone DB will be dropped by trap
