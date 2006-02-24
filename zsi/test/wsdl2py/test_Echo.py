#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
"""
Unittest 

WSDL:  
"""

CONFIG_FILE = 'config.txt'
SERVICE_NAME = 'EchoServer'
PORT_NAME = 'EchoServer'

sys.path.append('%s/%s' %(os.getcwd(), 'stubs'))

class EchoTest(unittest.TestCase):
    name = "test_Echo"
    done = False

    def setUp(self):
        if EchoTest.done: return
        EchoTest.done = True
        wsdl = os.path.abspath('../../samples/Echo/Echo.wsdl').strip()
        fin,fout = os.popen4('cd stubs; wsdl2py.py -f %s' %wsdl)
        # TODO: wait for wsdl2py.py to finish.
        for i in fout: print i
 
    def tearDown(self):
        pass

    def test_Echo(self):
        from EchoServer_services import EchoServerLocator, EchoRequest, EchoResponse
        port = EchoServerLocator().getEchoServer()
    

def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(EchoTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

