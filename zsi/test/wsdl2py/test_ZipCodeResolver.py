#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException

import utils
from paramWrapper import ResultsToStr

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
        """Done this way because unittest instantiates a TestCase
           for each test method, but want all diffs to go in one
           file.  Not doing testdiff as a global this way causes
           problems.
        """
        global testdiff

        if not testdiff:
            testdiff = utils.TestDiff(self, 'diffs')

    def test_CorrectedAddressHtml(self):
        request = portType.inputWrapper('CorrectedAddressHtml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = portType.CorrectedAddressHtml(request)
        print ResultsToStr(response)
    
    def test_CorrectedAddressXml(self):
        request = portType.inputWrapper('CorrectedAddressXml')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = portType.CorrectedAddressXml(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_FullZipCode(self):
        request = portType.inputWrapper('FullZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = portType.FullZipCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_ShortZipCode(self):
        request = portType.inputWrapper('ShortZipCode')
        request._address = '636 Colusa Avenue'
        request._city = 'Berkeley'
        request._state = 'California'
        response = portType.ShortZipCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_VersionInfo(self):
        request = portType.inputWrapper('VersionInfo')
        response = portType.VersionInfo(request)   
        testdiff.failUnlessEqual(ResultsToStr(response))


def makeTestSuite():
    global service, portType, testdiff

    testdiff = None
    kw = {}
    setUp = utils.TestSetUp('config.txt')
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


def tearDown():
    """Global tear down."""
    testdiff.close()

if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
