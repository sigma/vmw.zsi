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
    """Gets tests to run from configuration file."""
    global moduleList

    moduleList = []
    sys.path.append('.')
    cp = utils.TestSetUp('config.txt')
    for name, value in cp.items('individual_tests'):
        module = __import__(name)  # value unused for now
        moduleList.append(module)
    utils.TestProgram(defaultTest="makeTestSuite")

if __name__ == "__main__" : main()
    

