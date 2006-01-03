#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite

"""
Unittest for contacting the ZipCodeResolver Web service.

WSDL: http://webservices.eraserver.net/zipcoderesolver/zipcoderesolver.asmx?WSDL

"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'WSDL'
SERVICE_NAME = 'ZipCodeResolver'
PORT_NAME = 'ZipCodeResolverSoap'


class ZipCodeResolverTest(ServiceTestCase):
    """Test case for ZipCodeResolver Web service
    """
    name = "test_ZipCodeResolver"
    def setUp(self):
        self._portName = PORT_NAME
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
    
    def test_CorrectedAddressHtml(self):
        operationName = 'CorrectedAddressHtml'
        request = self.getInputMessageInstance(operationName)
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = self.RPC(operationName, request)

    def test_CorrectedAddressXml(self):
        operationName = 'CorrectedAddressXml'
        request = self.getInputMessageInstance(operationName)
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = self.RPC(operationName, request)
         
    def test_FullZipCode(self):
        operationName= 'FullZipCode'
        request = self.getInputMessageInstance(operationName)
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = self.RPC(operationName, request)
    
    def test_ShortZipCode(self):
        operationName = 'ShortZipCode'
        request = self.getInputMessageInstance(operationName)
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = self.RPC(operationName, request)
    
    def test_VersionInfo(self):
        operationName = 'VersionInfo'
        request = self.getInputMessageInstance(operationName)
        response = self.RPC(operationName, request)

    def _getPort(self, locator, netloc=None):
        """Returns a rpc proxy port instance.
           **Only expecting 1 service/WSDL, and 1 port/service.

           locator -- Locator instance
        """
        if len(self._wsm.services) != 1:
            raise TestException, 'only supporting WSDL with one service information item'
        methodNames = self._wsm.services[0].locator.getPortMethods()
        if len(methodNames) == 0:
            raise TestException, 'No port defined for service.'
        #elif len(methodNames) > 1:
        #    raise TestException, 'Not handling multiple ports.'
        callMethod = getattr(locator, methodNames[0])
        return callMethod(**self._getPortOptions(methodNames[0], locator, netloc))

def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(ZipCodeResolverTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
