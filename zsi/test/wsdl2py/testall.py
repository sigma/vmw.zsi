#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See Copyright for copyright notice!
###########################################################################
import unittest
import glob
import os.path
import sys

import utils

"""Runs all files beginning with test_ in this directory.
"""

def makeTestSuite():
    """Return a test suite containing all test cases in all test modules."""

    suite = unittest.TestSuite()
    for module in moduleList:
        suite.addTest(module.makeTestSuite())
    return suite


def main():
    """Searches the current directory for any modules matching test_*.py.
       Adapted from wxPython/wxPython/py/tests/testall.py."""
    global moduleList

    moduleList = []
    sys.path.append('.')
    for filename in glob.glob('test_*.py'):
        module = __import__(os.path.splitext(filename)[0])
        if not hasattr(module, 'SeparateTest'):
            moduleList.append(module)
    utils.TestProgram(defaultTest="makeTestSuite")

if __name__ == "__main__" : main()
    

