#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest
from ServiceTest import main, ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
"""
Unittest 

WSDL:  ../../samples/Echo/Echo.wsdl
"""

# General targets
def dispatch():
    """Run all dispatch tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(EchoTestCase, 'test_dispatch'))
    return suite

def local():
    """Run all local tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(EchoTestCase, 'test_local'))
    return suite

def net():
    """Run all network tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(EchoTestCase, 'test_net'))
    return suite
    
def all():
    """Run all tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(EchoTestCase, 'test_'))
    return suite


class EchoTestCase(ServiceTestCase):
    name = "test_EchoWSAddr200403"
    client_file_name = "EchoWSAddr200403Server_client.py"
    types_file_name  = "EchoWSAddr200403Server_types.py"
    server_file_name = "EchoWSAddr200403Server_server.py"

    def __init__(self, methodName):
        ServiceTestCase.__init__(self, methodName)
        self.wsdl2py_args.append('-a')
        self.wsdl2py_args.append('-b')
        self.wsdl2dispatch_args.append('-a')

    def getPortKWArgs(self):
        kw = ServiceTestCase.getPortKWArgs(self)
        kw['wsAddressURI'] = 'http://schemas.xmlsoap.org/ws/2004/03/addressing'
        return kw

    def test_local_Echo(self):
        msg = self.client_module.EchoRequest()
        rsp = self.client_module.EchoResponse()

    def test_dispatch_Echo(self):
        loc = self.client_module.EchoWSAddr200403ServerLocator()
        port = loc.getport(**self.getPortKWArgs())
        
        msg = self.client_module.EchoRequest()
        msg.EchoIn = 'bla bla bla'
        rsp = port.Echo(msg)
        self.failUnless(rsp.EchoResult == msg.EchoIn, "Bad Echo")


if __name__ == "__main__" :
    main()

