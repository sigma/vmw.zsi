#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

"""
Unittest for contacting the ZipCodeResolver Web service.

WSDL: http://webservices.eraserver.net/zipcoderesolver/zipcoderesolver.asmx?WSDL

"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'ZipCodeResolver'
PORT_NAME = 'ZipCodeResolverSoap'


class ZipCodeResolverTest(ServiceTestCase):
    """Test case for ZipCodeResolver Web service
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not ZipCodeResolverTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            ZipCodeResolverTest.service, ZipCodeResolverTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = ZipCodeResolverTest.portType

    def notest_CorrectedAddressHtml(self):
        request = self.portType.inputWrapper('CorrectedAddressHtml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        self.handleResponse(self.portType.CorrectedAddressHtml,request)

    def notest_CorrectedAddressXml(self):
        request = self.portType.inputWrapper('CorrectedAddressXml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        self.handleResponse(self.portType.CorrectedAddressXml,request,diff=True)
    
    def test_FullZipCode(self):
        request = self.portType.inputWrapper('FullZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        self.handleResponse(self.portType.FullZipCode,request,diff=True)
    
    def notest_ShortZipCode(self):
        request = self.portType.inputWrapper('ShortZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        self.handleResponse(self.portType.ShortZipCode,request,diff=True)
    
    def test_VersionInfo(self):
        request = self.portType.inputWrapper('VersionInfo')
        self.handleResponse(self.portType.VersionInfo,request,diff=True)   


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ZipCodeResolverTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
