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
Unittest for contacting the GlobalWeather portType for the
GlobalWeather Web service.

WSDL:  http://live.capescience.com/wsdl/GlobalWeather.wsdl
"""


class GlobalWeatherTest(unittest.TestCase):
    """Test case for GlobalWeather Web service, port type GlobalWeather
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

        # requires a floating point ZSI typecode; in progress
    def p_getWeatherReport(self):
        request = portType.inputWrapper('getWeatherReport')
            # airport code
        request._code = 'SFO'
        try:
            response = portType.getWeatherReport(request)
        except FaultException, msg:
            if not utils.failureException(FaultException, msg):
                return
        print ResultsToStr(response)

def makeTestSuite():
    global service, portType, testdiff

    testdiff = None
    kw = {}
    setUp = utils.TestSetUp('config.txt')
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
    utils.TestProgram(defaultTest="makeTestSuite")
