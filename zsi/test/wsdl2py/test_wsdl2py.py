#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import sys, unittest
import StringIO, os, getopt
from ZSI import wsdl2python
from ZSI.wstools.TimeoutSocket import TimeoutError
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wstools.Utility import HTTPResponse
from ServiceTest import CaseSensitiveConfigParser, TestDiff

"""
Tests wsdl2python code generation against most of the XMethods WSDL's.
"""
urlList = None
CONFIG_FILE = 'config.txt'
MODULE_DIR = 'generatedCode'

class Wsdl2pythonTest(unittest.TestCase):
    """Test case for wsdl2python.WriteServiceModule
    """

    environment = None

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        self.path = Wsdl2pythonTest.environment.next()
        print self.path
        sys.stdout.flush()

    def __str__(self):
        teststr = unittest.TestCase.__str__(self)
        if hasattr(self, "path"):
            return "%s: %s" % (teststr, self.path )
        else:
            return "%s" % (teststr)

    def test_code_generation(self):
        try:
            if self.path[:7] == 'http://':
                wsdl = WSDLReader().loadFromURL(self.path)
            else:
                wsdl = WSDLReader().loadFromFile(self.path)
        except TimeoutError:
            print "connection timed out"
            sys.stdout.flush()
            return
        except HTTPResponse:
            print "initial connection with service problem"
            sys.stdout.flush()
            return
        except:
            self.path = self.path + ": load failed, unable to start"
            raise
        codegen = wsdl2python.WriteServiceModule(wsdl)
        f_types, f_services = codegen.get_module_names()
        hasSchema = len(codegen._wa.getSchemaDict())

        if hasSchema:
            strFile = StringIO.StringIO()
            typesFileName = f_types + ".py"
            testdiff = TestDiff(self, MODULE_DIR, typesFileName)
            try:
                codegen.write_service_types(f_types, strFile)
            except:
                self.path = self.path + ": write_service_types"
                raise
            if strFile.closed:
                print "trouble"
            testdiff.failUnlessEqual(strFile)
            strFile.close()

        strFile = StringIO.StringIO()
        servicesFileName = f_services + ".py"
        testdiff = TestDiff(self, MODULE_DIR, servicesFileName)
        try:
            signatures = codegen.write_services(f_types,
                             f_services, strFile, hasSchema)
        except:
            self.path = self.path + ": write_services"
            raise
        testdiff.failUnlessEqual(strFile)
        strFile.close()


def getUrls():
        # remove command-line arguments that unittest doesn't know
        # how to handle
    options, args = getopt.getopt(sys.argv[1:], 'hHdv',
                                          ['help'])
    for i in range(len(sys.argv)-1, 0, -1):
        if sys.argv[i] in args:
            del sys.argv[i]
    if len(args) == 0:
        args = ['no_schemas', 'simple_types', 'complex_types']

    urlList = []
    cp = CaseSensitiveConfigParser()
    cp.read(CONFIG_FILE)
    for arg in args:
        if cp.has_section(arg):
            for name, value in cp.items(arg):
                urlList.append(value)
    return urlList


def makeTestSuite(section=None):
    suite = unittest.TestSuite()
    Wsdl2pythonTest.environment = iter(urlList)
    urlLen = len(urlList)
    for i in range(0, urlLen):
        suite.addTest(unittest.makeSuite(Wsdl2pythonTest, 'test_'))
    return suite

def main():
    global urlList

    urlList = getUrls()
    unittest.TestProgram(defaultTest="makeTestSuite")
                  
if __name__ == "__main__" :
    main()
