#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Blender tests

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

Blender tests
"""

blender = {'2.65': '/opt/blender265/blender', 
           '2.66': '/opt/blender266a/blender',
           '2.67': '/opt/blender267/blender' }

import subprocess
import os.path

def runTest(suite):
    for blenderv, blenderexec in blender.items():
        testBlender(blenderv, blenderexec, suite)

def getPath():
    # TODO properly resolve path
    return 'testsuite'

def testBlender(version, execPath, suite):
    blender_script = os.path.join(getPath(), 'blender_initTest.py')
    args = [execPath, '--debug', '-P', blender_script]

    bp = subprocess.Popen(args, bufsize=0, executable=None, stdin=None,
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    shell=False, cwd=None, env=None, universal_newlines=True)

    stdout, _ = bp.communicate()
    stdout = stdout.split('\n')

    testOutput = []
    for line in stdout:
        line = line.strip()
        if line.startswith('MH_TEST'):
            testOutput.append(line)

    for entry in testOutput:
        entry = entry.split()
        result = entry[1]
        msg = entry[2:]
        suite.addResult('Blender %s' % version, 'Import plugin', result, msg)

