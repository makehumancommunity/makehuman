#!/bin/bash

##
# Retrieve the (oldest) release tag which contains the specified
# changeset.
#
# Usage: hg_get_release.sh changeset_hash
##

function contains() { 
    if [ "$(hg log -r $1 -b $2)" == "" ] ; 
    then
        # false
        return 15
    else
        # true
        return 0
    fi; 
}

if contains stable $1 stable ; then
    echo "stable"
else
    echo "unstable"
fi

TAGS=$( hg tags | awk '{ print $1 }' | tac )
for TAG in $TAGS
do
    if hg log -r "descendants($1) and $TAG" | grep -q changeset; then
        echo $TAG
        exit
    fi
done

