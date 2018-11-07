#!/usr/bin/python3

import os
import sys
import subprocess

scriptpath = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
mhpath = os.path.join(scriptpath, "makehuman")
os.chdir(mhpath)
subprocess.call([sys.executable,"makehuman.py"])

