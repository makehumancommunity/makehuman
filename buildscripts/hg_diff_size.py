#!/usr/bin/python2.7

##
# Calculate the size in bytes of a hg changeset diff
#
# Example:
#   hg diff -r tip | buildscripts/hg_diff_size.py
##

import fileinput

def is_diff_line(line):
    return (line.startswith('-') and not line.startswith('--- ')) or \
        (line.startswith('+') and not line.startswith('+++ '))

filename = None
f = fileinput.input()
try:
    for line in f:
        if f.isfirstline():
            if filename:
                print filename,": size changed by", size_diff, "bytes."

            size_diff = 0
            line_diff = 0
            filename = f.filename()

        if is_diff_line(line):
            size_diff += len(line[1:])
            line_diff += 1

    if filename:
        print filename,": size changed by", size_diff, "bytes. %s lines changed" % line_diff

finally:
    f.close()
