#!/bin/bash

##
# Test whether a mercurial branch contains a specific
# commit or changeset.
#
# Usage: hg_contains.sh branchname changeset_id

function contains() { 
    if [ "$(hg log -r $1 -b $2)" == "" ] ; 
    then 
        echo no; 
    else 
        echo yes ; 
    fi; 
}

contains $2 $1
