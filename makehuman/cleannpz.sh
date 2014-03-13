#!/bin/bash

##
# Clean up any remaining .npz files.
##

find . -type f -iname \*.npz -exec rm -rf {} \;


# And .bin files

find . -type f -iname \*.bin -exec rm -rf {} \;
