#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

"""
Unittest for contacting the StationInfo portType of the GlobalWeather
Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'GlobalWeather'
PORT_NAME = 'StationInfo'


class StationInfoTest(ServiceTestCase):
    """Test case for GlobalWeather Web service, port type StationInfo
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not StationInfoTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            StationInfoTest.service, StationInfoTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = StationInfoTest.portType

    def test_getStation(self):
        request = self.portType.inputWrapper('getStation')
        request._code = 'SFO'
        self.handleResponse(self.portType.getStation,request,diff=True)
    
    def test_isValidCode(self):
        request = self.portType.inputWrapper('isValidCode')
        request._code = 'SFO'
        self.handleResponse(self.portType.isValidCode,request,diff=True)
    
    def test_listCountries(self):
        request = self.portType.inputWrapper('listCountries')
        self.handleResponse(self.portType.listCountries,request,diff=True)

    def test_searchByCode(self):
        request = self.portType.inputWrapper('searchByCode')
        request._code = 'SFO'
        self.handleResponse(self.portType.searchByCode,request,diff=True)
    
    def test_searchByCountry(self):
        request = self.portType.inputWrapper('searchByCountry')
        request._country = 'Australia'
        self.handleResponse(self.portType.searchByCountry,request,diff=True)
    
        # can't find what valid name is, returns empty result
    def notest_searchByName(self):
        request = self.portType.inputWrapper('searchByName')
        request._name = 'San Francisco Airport'
        self.handleResponse(self.portType.searchByName,request,diff=True)
    
        # can't find what valid region is, returns empty result
    def notest_searchByRegion(self):
        request = self.portType.inputWrapper('searchByRegion')
        request._region = 'Europe'
        self.handleResponse(self.portType.searchByRegion,request,diff=True)


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StationInfoTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
