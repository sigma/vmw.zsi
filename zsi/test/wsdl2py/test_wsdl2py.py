#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import sys, ConfigParser, unittest
import StringIO, os
import py_compile
from ZSI import wsdl2python
from ZSI.wstools.TimeoutSocket import TimeoutError
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wstools.Utility import HTTPResponse

import utils

"""
Tests wsdl2python code generation and compilation against
most of the XMethods WSDL's.
"""

class Wsdl2pythonTest(unittest.TestCase):
    """Test case for wsdl2python.WriteServiceModule
    """

    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        global configLoader

        self.path = configLoader.nameGenerator.next()
        print self.path
        sys.stdout.flush()

    def __str__(self):
        teststr = unittest.TestCase.__str__(self)
        if hasattr(self, "path"):
            return "%s: %s" % (teststr, self.path )
        else:
            return "%s" % (teststr)


    def test_code_generation(self):
        global servicesFileName, typesFileName

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
            print "intial connection with service problem"
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
            testdiff = utils.TestDiff(self, 'generatedCode', typesFileName)
            try:
                codegen.write_service_types(f_types, strFile)
            except:
                self.path = self.path + ": write_service_types"
                raise
            if strFile.closed:
                print "trouble"
            testdiff.failUnlessEqual(strFile)
            strFile.close()
        else:
            typesFileName = None

        strFile = StringIO.StringIO()
        servicesFileName = f_services + ".py"
        testdiff = utils.TestDiff(self, 'generatedCode', servicesFileName)
        try:
            signatures = codegen.write_services(f_types,
                             f_services, strFile, hasSchema)
        except:
            self.path = self.path + ": write_services"
            raise
        testdiff.failUnlessEqual(strFile)
        strFile.close()


    def test_compile_0types(self):
        if not typesFileName:
            return
        try:
            py_compile.compile(
                'generatedCode' + os.sep + typesFileName,
                doraise=True)

            # py_compile.compile raises bogus indentation exceptions
        except py_compile.PyCompileError, err:
            if err.msg.find('IndentationError') != -1:
                pass
            else:
                raise


    def test_compile_1services(self):
        if not servicesFileName:
            return
        try:
            py_compile.compile(
                'generatedCode' + os.sep + servicesFileName,
                doraise=True)

            # py_compile.compile raises bogus indentation exceptions
        except py_compile.PyCompileError, err:
            if err.msg.find('IndentationError') != -1:
                pass
            else:
                raise



def makeTestSuite(section=None):
    global configLoader
    global servicesFileName
    global typesFileName

    servicesFileName = None
    typesFileName = None

    suite = unittest.TestSuite()
    configLoader = utils.MatchTestLoader(False, "config.txt", "Wsdl2pythonTest")
    if not section:
        found = configLoader.setSection(sys.argv)
        if not found:
            configLoader.setSection(["no_schemas", "simple_types",
                                     "complex_types"])
    else:
        configLoader.setSection(section)
    suite.addTest(configLoader.loadTestsFromConfig(Wsdl2pythonTest))
    return suite


def main():
    loader = utils.MatchTestLoader(False, "config.txt", "makeTestSuite")
    utils.TestProgram(defaultTest="makeTestSuite", testLoader=loader)
                  

if __name__ == "__main__" :
    main()
