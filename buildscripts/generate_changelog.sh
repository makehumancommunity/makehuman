#!/bin/bash

##
# Generate a changelog for a release newer than tag name specified on commandline
# Usage: for example, to generate a changeset for v1.0.2, which should list the
# changes since previous release 1.0.1, use the follow command:
#    generate_changelog.sh 1.0.1
#
# To list the changes between two tags, for example the changesets committed
# after the v1.0.0 tag, up until the creation of the 1.0.1 tag:
#    generate_changelog.sh 1.0.0 1.0.1
##

if [[ -z "$2" ]]; then
    echo '1'
    hg log -r "branch(stable) - ancestors(tag($1))" --style changelog > changelog.txt
else
    echo '2'
    hg log -r $1:$2 -b stable --style changelog > changelog.txt
fi

