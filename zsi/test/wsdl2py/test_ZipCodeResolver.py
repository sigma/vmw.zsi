#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException

import utils
from paramWrapper import ParamWrapper
from clientGenerator import ClientGenerator

"""
Unittest for contacting the ZipCodeResolver Web service.
Note that unittest calls setUp and tearDown after each
test method, hence the globals.

WSDL: http://webservices.eraserver.net/zipcoderesolver/zipcoderesolver.asmx?WSDL

"""


class ZipCodeResolverTest(unittest.TestCase):
    """Test case for ZipCodeResolver Web service
    """

    def setUp(self):
        """unittest calls setUp and tearDown after each
           test method call.
        """
        global testdiff
        global ZipCodeResolverSoap

        kw = {}
        ZipCodeResolverSoap = service.ZipCodeResolverLocator().getZipCodeResolverSoap(**kw)

        if not testdiff:
            testdiff = utils.TestDiff(self, 'generatedCode')
            testdiff.setDiffFile('ZipCodeResolver.diffs')
    
    def test_CorrectedAddressHtml(self):
        request = service.CorrectedAddressHtmlSoapInWrapper()
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = ZipCodeResolverSoap.CorrectedAddressHtml(request)
        print ParamWrapper(response)
    
    def test_CorrectedAddressXml(self):
        request = service.CorrectedAddressXmlSoapInWrapper()
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = ZipCodeResolverSoap.CorrectedAddressXml(request)
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def test_FullZipCode(self):
        request = service.FullZipCodeSoapInWrapper()
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = ZipCodeResolverSoap.FullZipCode(request)
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def test_ShortZipCode(self):
        request = service.ShortZipCodeSoapInWrapper()
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = ZipCodeResolverSoap.ShortZipCode(request)
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def test_VersionInfo(self):
        request = service.VersionInfoSoapInWrapper()
        response = ZipCodeResolverSoap.VersionInfo(request)   
        testdiff.failUnlessEqual(ParamWrapper(response))


def setUp():
    global testdiff
    global deleteFile
    global service

    deleteFile = utils.handleExtraArgs(sys.argv[1:])
    testdiff = None
    service = ClientGenerator().getModule('complex_types',
                                          'ZipCodeResolver', 'generatedCode')
    return service



def makeTestSuite():
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(ZipCodeResolverTest, 'test_'))
    return suite


def main():
    if setUp():
        utils.TestProgram(defaultTest="makeTestSuite")
                  

if __name__ == "__main__" : main()
