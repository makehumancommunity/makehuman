#!/usr/bin/python3

# On ubuntu you need "apt-get install pylint3" and the command is called
# "pylint3". On other platforms you might want to change this.
# 
# I never tested if this even works on windows. 

PYLINT="pylint3"

import os

pythonfiles = []

for dirName, subdirList, fileList in os.walk("."):
    for fname in fileList:
        filename, ext = os.path.splitext(fname)
        if ext == ".py":
            pythonfiles.append( os.path.join(dirName,fname) )

os.system(PYLINT + " > pylint.log " + " ".join(pythonfiles))

