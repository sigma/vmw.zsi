#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import sys, unittest
import os
import py_compile

#import utils

"""
Tests compilation of wsdl2python generated code.
"""

CONFIG_FILE = 'config.txt'
MODULE_DIR = 'generatedCode'

class CompileCodeTest(unittest.TestCase):
    """Test case for compiling modules resulting from call
       to wsdl2python.WriteServiceModule
    """

    environment = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        self.fname = CompileCodeTest.environment.next()
        print self.fname
        sys.stdout.flush()

    def __str__(self):
        teststr = unittest.TestCase.__str__(self)
        if hasattr(self, "fname"):
            return "%s: %s" % (teststr, self.fname)
        else:
            return "%s" % (teststr)

    def test_compile(self):
        if not self.fname:
            return
        try:
            py_compile.compile(self.fname, doraise=True)

            # py_compile.compile raises bogus indentation exceptions
        except py_compile.PyCompileError, err:
            if err.msg.find('IndentationError') != -1:
                pass
            else:
                raise

def getFiles():
    cmd = "ls %s*.py" % (MODULE_DIR + os.sep)
    result = os.popen(cmd)
    fnameList = []
    for fname in result.readlines():
         fnameList.append(fname[:-1])
    return fnameList

def makeTestSuite():
    suite = unittest.TestSuite()
    fnameList = getFiles()
    CompileCodeTest.environment = iter(fnameList)
    listLen = len(fnameList)
    for i in range(0, listLen):
        suite.addTest(unittest.makeSuite(CompileCodeTest, 'test_'))
    return suite


def main():
    unittest.TestProgram(defaultTest="makeTestSuite")
                  
if __name__ == "__main__" :
    main()
