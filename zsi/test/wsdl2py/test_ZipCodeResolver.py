#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException

from utils import TestSetUp, TestProgram, TestDiff, failureException
from paramWrapper import ResultsToStr

"""
Unittest for contacting the ZipCodeResolver Web service.

WSDL: http://webservices.eraserver.net/zipcoderesolver/zipcoderesolver.asmx?WSDL

"""


class ZipCodeResolverTest(unittest.TestCase):
    """Test case for ZipCodeResolver Web service
    """

    def notest_CorrectedAddressHtml(self):
        request = portType.inputWrapper('CorrectedAddressHtml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        try:
            response = portType.CorrectedAddressHtml(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    

    def notest_CorrectedAddressXml(self):
        request = portType.inputWrapper('CorrectedAddressXml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        try:
            response = portType.CorrectedAddressXml(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def test_FullZipCode(self):
        request = portType.inputWrapper('FullZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        try:
            response = portType.FullZipCode(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def notest_ShortZipCode(self):
        request = portType.inputWrapper('ShortZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        try:
            response = portType.ShortZipCode(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def test_VersionInfo(self):
        request = portType.inputWrapper('VersionInfo')
        try:
            response = portType.VersionInfo(request)   
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))


def makeTestSuite():
    global service, portType

    kw = {}
    setUp = TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'ZipCodeResolver')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = setUp.setService(ZipCodeResolverTest, serviceLoc,
                                  'ZipCodeResolver', 'ZipCodeResolverSoap',
                                  **kw)
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(ZipCodeResolverTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
