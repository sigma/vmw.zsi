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

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'individual_tests'

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
    cp = utils.CaseSensitiveConfigParser()
    cp.read(CONFIG_FILE)
    for name, value in cp.items(CONFIG_SECTION):
        module = __import__(name)  # value unused for now
        moduleList.append(module)
    utils.TestProgram(defaultTest="makeTestSuite")

if __name__ == "__main__" : main()
    

