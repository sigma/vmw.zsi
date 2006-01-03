#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See Copyright for copyright notice!
###########################################################################
import  unittest, optparse
from ServiceTest import CONFIG_PARSER, DOCUMENT, LITERAL, BROKE, TESTS


def makeTestSuite(document=None, literal=None, broke=None):
    """Return a test suite containing all test cases that satisfy 
    the parameters. None means don't check.

       document -- None, True, False
       literal -- None, True, False
       broke -- None, True, False
    """
    cp = CONFIG_PARSER
    testSections = []
    sections = ['rpc_encoded' , 'rpc_encoded_broke',
                'rpc_literal', 'rpc_literal_broke', 'rpc_literal_broke_interop',
                'doc_literal', 'doc_literal_broke', 'doc_literal_broke_interop',
                ]
    for section in sections:
    
        if (document is not None) and (cp.getboolean(section, DOCUMENT) is not document):
            pass
        elif (literal is not None) and (cp.getboolean(section, LITERAL) is not literal):
            pass
        elif (broke is not None) and (cp.getboolean(section, BROKE) is not broke):
            pass
        else:
            testSections.append(section)
        
    suite = unittest.TestSuite()
    for section in testSections:
        moduleList = cp.get(section, TESTS).split()
        for module in  map(__import__, moduleList):
            s = module.makeTestSuite()
            suite.addTest(s)
    return suite

def brokeTestSuite():
    return makeTestSuite(broke=True)

def workingTestSuite():
    return makeTestSuite(broke=False)

def docLitTestSuite():
    return makeTestSuite(broke=False, document=True, literal=True)

def rpcLitTestSuite():
    return makeTestSuite(broke=False, document=False, literal=True)

def rpcEncTestSuite():
    return makeTestSuite(broke=False, document=False, literal=False)

def collectTests():
    suite = unittest.TestSuite()
    suite.addTest(brokeTestSuite())
    suite.addTest(workingTestSuite())
    suite.addTest(docLitTestSuite())
    return suite

def main():
    """Gets tests to run from configuration file.
    """
    unittest.TestProgram(defaultTest="workingTestSuite")

if __name__ == "__main__" : main()
    

