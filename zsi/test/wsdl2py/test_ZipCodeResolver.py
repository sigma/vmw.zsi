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

# General targets
def dispatch():
    """Run all dispatch tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_dispatch'))
    return suite

def local():
    """Run all local tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_local'))
    return suite

def net():
    """Run all network tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_net'))
    return suite
    
def all():
    """Run all tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_'))
    return suite


class ZipCodeResolverTest(ServiceTestCase):
    """Test case for ZipCodeResolver Web service
    """
    name = "test_ZipCodeResolver"
    
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


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="all")

