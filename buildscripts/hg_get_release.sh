#!/bin/bash

##
# Retrieve the (oldest) release tag which contains the specified
# changeset.
#
# Usage: hg_get_release.sh changeset_hash
##

TAGS=$( hg tags | awk '{ print $1 }' | tac )
for TAG in $TAGS
do
    #echo $TAG
    if hg log -r "descendants($1) and $TAG" | grep -q changeset; then
        echo $TAG
        exit
    fi
done

