#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

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

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not GlobalWeatherTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            GlobalWeatherTest.service, GlobalWeatherTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = GlobalWeatherTest.portType


        # requires a floating point ZSI typecode; in progress
    def notest_getWeatherReport(self):
        request = self.portType.inputWrapper('getWeatherReport')
            # airport code
        request._code = 'SFO'
        try:
            self.failUnlessRaises(EvaluateException, self.portType.getWeatherReport, request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        """
        self.handleResponse(self.portType.getWeatherReport,request)
        """


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GlobalWeatherTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
