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

        # problem with 'NaN' in pressure._delta field
        # not a valid response - not fixable on our end
    def p_getWeatherReport(self):
        request = portType.inputWrapper('getWeatherReport')
            # airport code
        request._code = 'SFO'
        response = portType.getWeatherReport(request)
        print ResultsToStr(response)

def makeTestSuite():
    global service, portType, testdiff

    service, portType = \
        utils.testSetUp(GlobalWeatherTest, 'GlobalWeather', 'GlobalWeather')
    testdiff = None

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(GlobalWeatherTest, 'test_'))
    return suite


def tearDown():
    """Global tear down."""

if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
