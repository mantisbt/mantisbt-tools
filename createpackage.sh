#!/bin/bash
#
# Original script supplied by:
# Tais M. Hansen <tais.hansen@osd.dk>#
#

set -e

SVNREPOS="http://mantisbt.svn.sourceforge.net/svnroot/mantisbt/tags"

function digest {
    file=$(basename $1)
    path=$(dirname $1)
    pushd $path >/dev/null
    cat > $file.DIGESTS << EODIGESTS
# MD5 HASH
$(md5sum --binary $file)
# SHA1 HASH
$(sha1sum --binary $file)
EODIGESTS
    popd >/dev/null
}

function usage {
    cat << EOUSAGE
Syntax: $0 [options] <tag>

Options:
  -h        This help.
  -r name   Release name. Defaults to MANTIS_VERSION in core/constant_inc.php
            for the given <tag>.
  -c        Remove downloaded directory after package creation
EOUSAGE
}

# Options.
declare tag=""
declare tag_path=""
declare release=""
declare release_path=""
declare cleanup=""

# Parse commandline options.
while getopts hcr: opt; do
    case ${opt} in
        r)
            release="${OPTARG}"
            ;;
        c)
            cleanup="yes"
            ;;
        h|?)
            usage
            exit 1
            ;;
    esac
done

# Remaining argument should be the requested tag.
shift $((${OPTIND}-1))
tag="$1"

# Make sure we have a tag before continuing.
if [ -z "${tag}" ]; then
    echo "Error: Tag not specified."
    usage
    exit 1
fi

# Retrieve code, if we don't have it already.
echo "Retrieving ${tag} from ${SVNREPOS}."
tag_path="$(pwd)/mantis-${tag}"
if [[ -d "${tag_path}" ]]; then
    echo "Error: Tag directory already exists: ${tag_path}"
    exit 1
fi
svn export --quiet --native-eol LF "${SVNREPOS}/${tag}" "${tag_path}"

# Retrieve release name.
if [[ -z "${release}" ]]; then
    echo "Attempting to retrieve release name."
    pushd ${tag_path} >/dev/null
    release=$(php -r 'include "core/constant_inc.php"; echo MANTIS_VERSION;')
#release=$(awk "/MANTIS_VERSION/{if(match(\$0, /define\(.*'MANTIS_VERSION'.*'([^']+)'.*\);/, m)){print m[1];}}" core/constant_inc.php)
    popd >/dev/null
    if [[ -z "${release}" ]]; then
        echo "Error: Failed to parse MANTIS_VERSION in core/constant_inc.php"
        exit 1
    fi
fi
echo "Release: ${release}"

# Prepare release dir.
echo "Preparing release directory."
release_name="mantis-${release}"
release_path="$(pwd)/${release_name}"
if [[ -d "${release_path}" ]]; then
    echo "Error: Release directory already exists: ${release_path}"
    exit 1
fi
mv "${tag_path}" "${release_path}"

# Sanitize.
echo "Sanitizing."
pushd "${release_path}" >/dev/null
rm -rf packages

echo "Looking for executable files..."
find . -type f -perm /111 -print -exec chmod -x {} \;
popd >/dev/null

# Generate archives and digests.
echo "Generating tar-archive and digests."
tar czf "${release_name}.tar.gz" "${release_name}"
digest "${release_name}.tar.gz"

echo "Generating zip-archive and digests."
zip -qr "${release_name}.zip" "${release_name}"
digest "${release_name}.zip"

# Show resulting archives and digest-files.
ls -l ${release_name}.tar.gz*
ls -l ${release_name}.zip*

# Cleanup.
if [[ -n $cleanup ]]; then
    echo "Cleaning up."
    rm -rf "${release_path}"
fi

echo "All done."
