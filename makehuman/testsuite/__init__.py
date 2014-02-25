#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Testing suite

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Integrated application testing suite
"""

# TODO use unittest module for some or all tests

class TestSuite(object):
    def __init__(self):
        self.testResults = []

    def addResult(self, testPackage, testName, status, msg):
        self.testResults.append( (testPackage, testName, status, msg) )


suite = None


def runAll():
    global suite
    suite = TestSuite()

    import test_blender
    test_blender.runTest(suite)

    printResults()

def printResults():
    global suite
    success = 0
    failed = 0
    warning = 0
    for result in suite.testResults:
        status = result[2]
        if status.lower() == 'success':
            success += 1
        elif status.lower() == 'warning':
            warning += 1
        elif status.lower() == 'error':
            failed += 1
            print 'Test %s %s FAILED: %s' % (result[0], result[1], result[3])
        else:
            print "Test error: unknown status: %s" % status

    print "Test results:"
    total = success + warning + failed
    print "Successful: %s/%s (%s%%)" % (success, total, int((float(success)/total)*100))
    print "Failed: %s/%s (%s%%)" % (failed, total, int((float(failed)/total)*100))
    print "Warnings: %s/%s (%s%%)" % (warning, total, int((float(warning)/total)*100))
