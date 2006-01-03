#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
"""
Unittest for contacting the GlobalWeather portType for the
GlobalWeather Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'GlobalWeather'
PORT_NAME = 'GlobalWeather'


class GlobalWeatherTest(ServiceTestCase):
    """Test case for GlobalWeather Web service, port type GlobalWeather
    """

    name = "test_GlobalWeather_gw"
    
    def setUp(self):
        self._portName = "GlobalWeather"
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
        
        
    
           # requires a floating point ZSI typecode; in progress
    def test_getWeatherReport(self):
        """
        This test raises a ZSI.EvaluateException
        """
        operationName = "getWeatherReport"
        request = self.getInputMessageInstance(operationName)
        request._code = 'SFO'
        self.RPC(operationName, request)    
    


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(GlobalWeatherTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
