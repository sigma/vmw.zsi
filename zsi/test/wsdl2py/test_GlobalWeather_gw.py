#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import EvaluateException, FaultException

from utils import TestSetUp, TestProgram, failureException
from paramWrapper import ResultsToStr

"""
Unittest for contacting the GlobalWeather portType for the
GlobalWeather Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""


class GlobalWeatherTest(unittest.TestCase):
    """Test case for GlobalWeather Web service, port type GlobalWeather
    """

        # requires a floating point ZSI typecode; in progress
    def test_getWeatherReport(self):
        request = portType.inputWrapper('getWeatherReport')
            # airport code
        request._code = 'SFO'
        try:
            self.failUnlessRaises(EvaluateException, portType.getWeatherReport, request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        """
        try:
            response = portType.getWeatherReport(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
        """


def makeTestSuite():
    global service, portType

    kw = {}
    setUp = TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'GlobalWeather')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = \
        setUp.setService(GlobalWeatherTest, serviceLoc,
                       'GlobalWeather', 'GlobalWeather', **kw)

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(GlobalWeatherTest, 'test_'))
    return suite


def tearDown():
    """Global tear down."""

if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
