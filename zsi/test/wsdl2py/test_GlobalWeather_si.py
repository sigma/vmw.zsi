#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import EvaluateException

import utils
from paramWrapper import ResultsToStr

"""
Unittest for contacting the StationInfo portType of the GlobalWeather
Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""


class StationInfoTest(unittest.TestCase):
    """Test case for GlobalWeather Web service, port type StationInfo
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

    def test_getStation(self):
        request = portType.inputWrapper('getStation')
        request._code = 'SFO'
        response = portType.getStation(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_isValidCode(self):
        request = portType.inputWrapper('isValidCode')
        request._code = 'SFO'
        response = portType.isValidCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_listCountries(self):
        request = portType.inputWrapper('listCountries')
        response = portType.listCountries(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_searchByCode(self):
        request = portType.inputWrapper('searchByCode')
        request._code = 'SFO'
        response = portType.searchByCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_searchByCountry(self):
        request = portType.inputWrapper('searchByCountry')
        request._country = 'Australia'
        response = portType.searchByCountry(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
        # can't find what valid name is, returns empty result
    def test_searchByName(self):
        request = portType.inputWrapper('searchByName')
        request._name = 'San Francisco Airport'
        response = portType.searchByName(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
        # can't find what valid region is, returns empty result
    def test_searchByRegion(self):
        request = portType.inputWrapper('searchByRegion')
        request._region = 'Europe'
        response = portType.searchByRegion(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    

def makeTestSuite():
    global service, portType, testdiff

    service, portType = \
        utils.testSetUp(StationInfoTest, 'GlobalWeather', 'StationInfo')
    testdiff = None

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(StationInfoTest, 'test_'))
    return suite


def tearDown():
    """Global tear down."""
    testdiff.close()


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
