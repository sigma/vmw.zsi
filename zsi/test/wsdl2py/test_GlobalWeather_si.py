#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
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
    
    name = "test_GlobalWeather_si"

    def setUp(self):
        self._portName = "StationInfo"
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)

    def test_getStation(self):
        operationName = "getStation"
        request = self.getInputMessageInstance(operationName)    
        request._code = 'SFO'
        self.RPC(operationName, request)
    
    def test_isValidCode(self):
        operationName = "isValidCode"
        request = self.getInputMessageInstance(operationName)
        request._code = 'SFO'
        self.RPC(operationName, request)
    
    def test_listCountries(self):
        operationName = "listCountries"
        request = self.getInputMessageInstance(operationName)
        self.RPC(operationName, request)
        
    def test_searchByCode(self):
        operationName = 'searchByCode'
        request = self.getInputMessageInstance(operationName)
        request._code = 'SFO'
        self.RPC(operationName, request)
    
    def test_searchByCountry(self):
        operationName = 'searchByCountry'
        request = self.getInputMessageInstance(operationName)
        request._country = 'Australia'
        self.RPC(operationName, request)
    
        # can't find what valid name is, returns empty result
    def test_searchByName(self):
        operationName = 'searchByName'
        request = self.getInputMessageInstance(operationName)
        request._name = 'San Francisco Airport'
        self.RPC(operationName, request)
    
        # can't find what valid region is, returns empty result
    def test_searchByRegion(self):
        operationName = 'searchByRegion'
        request = self.getInputMessageInstance(operationName)
        request._region = 'Europe'
        self.RPC(operationName, request)


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(StationInfoTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
