#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import EvaluateException

import utils
from paramWrapper import ResultsToStr
from clientGenerator import ClientGenerator

"""
Unittest for contacting the GlobalWeather Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""


class GlobalWeatherTest(unittest.TestCase):
    """Test case for GlobalWeather Web service
    """

    def setUp(self):
        """unittest calls setUp and tearDown after each
           test method call.
        """
        global testdiff
        global StationInfo
        global GlobalWeather

        if not testdiff:
            testdiff = utils.TestDiff(self, 'diffs')
            testdiff.setDiffFile('GlobalWeather.diffs')

        kw = {}
        #kw = { 'tracefile' : sys.stdout }
        StationInfo = service.GlobalWeatherLocator().getStationInfo(**kw)
        GlobalWeather = service.GlobalWeatherLocator().getGlobalWeather(**kw)

    
        # problem with 'NaN' in pressure._delta field
        # not a valid response - not fixable on our end
    def p_getWeatherReport(self):
        request = service.getWeatherReportWrapper()
            # airport code
        request._code = 'SFO'
        response = GlobalWeather.getWeatherReport(request)
        print ResultsToStr(response)

    def test_getStation(self):
        request = service.getStationWrapper()
        request._code = 'SFO'
        response = StationInfo.getStation(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_isValidCode(self):
        request = service.isValidCodeWrapper()
        request._code = 'SFO'
        response = StationInfo.isValidCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_listCountries(self):
        request = service.listCountriesWrapper()
        response = StationInfo.listCountries(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_searchByCode(self):
        request = service.searchByCodeWrapper()
        request._code = 'SFO'
        response = StationInfo.searchByCode(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
    def test_searchByCountry(self):
        request = service.searchByCountryWrapper()
        request._country = 'Australia'
        response = StationInfo.searchByCountry(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
        # can't find what valid name is, returns empty result
    def test_searchByName(self):
        request = service.searchByNameWrapper()
        request._name = 'San Francisco Airport'
        response = StationInfo.searchByName(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    
        # can't find what valid region is, returns empty result
    def test_searchByRegion(self):
        request = service.searchByRegionWrapper()
        request._region = 'Europe'
        response = StationInfo.searchByRegion(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    

def setUp():
    global testdiff
    global deleteFile
    global service

    deleteFile = utils.handleExtraArgs(sys.argv[1:])
    testdiff = None
    service = ClientGenerator().getModule('config.txt', 'complex_types',
                                          'GlobalWeather', 'generatedCode')
    return service

def makeTestSuite():
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(GlobalWeatherTest, 'test_'))
    return suite


def main():
    if setUp():
        utils.TestProgram(defaultTest="makeTestSuite")
                  

if __name__ == "__main__" : main()
