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
Unittest for contacting the StationInfo portType of the GlobalWeather
Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""


class StationInfoTest(unittest.TestCase):
    """Test case for GlobalWeather Web service, port type StationInfo
    """

    def test_getStation(self):
        request = portType.inputWrapper('getStation')
        request._code = 'SFO'
        try:
            response = portType.getStation(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def test_isValidCode(self):
        request = portType.inputWrapper('isValidCode')
        request._code = 'SFO'
        try:
            response = portType.isValidCode(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def test_listCountries(self):
        request = portType.inputWrapper('listCountries')
        try:
            response = portType.listCountries(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))
    

    def test_searchByCode(self):
        request = portType.inputWrapper('searchByCode')
        request._code = 'SFO'
        try:
            response = portType.searchByCode(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
    def test_searchByCountry(self):
        request = portType.inputWrapper('searchByCountry')
        request._country = 'Australia'
        try:
            response = portType.searchByCountry(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    
        # can't find what valid name is, returns empty result
    def notest_searchByName(self):
        request = portType.inputWrapper('searchByName')
        request._name = 'San Francisco Airport'
        try:
            response = portType.searchByName(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))

    
        # can't find what valid region is, returns empty result
    def notest_searchByRegion(self):
        request = portType.inputWrapper('searchByRegion')
        request._region = 'Europe'
        try:
            response = portType.searchByRegion(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))
    

def makeTestSuite():
    global service, portType

    kw = {}
    setUp = TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'GlobalWeather')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = \
        setUp.setService(StationInfoTest, serviceLoc,
                         'GlobalWeather', 'StationInfo', **kw)

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(StationInfoTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
