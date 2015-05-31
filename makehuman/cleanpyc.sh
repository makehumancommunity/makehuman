#!/bin/bash

##
# Clean up any remaining .pyc files.
# It is advised to do this after every svn update.
##

find . -type f -iname \*.pyc -exec rm -rf {} \;
