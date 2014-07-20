#!/bin/bash

##
# Generate a changelog for a release newer than tag name specified on commandline
# Usage: for example, to generate a changeset for v1.0.2, which should list the
# changes since previous release 1.0.1, use the follow command:
#    generate_changelog.sh 1.0.1
##

hg log -r "branch(stable) - ancestors(tag($1))" --style changelog > changelog.txt
