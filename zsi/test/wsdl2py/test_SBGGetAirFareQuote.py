#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
import time
from ZSI import EvaluateException

import utils
from paramWrapper import ResultsToStr

"""
Unittest for contacting the SBGGetAirFareQuoteService Web service.

WSDL: http://wavendon.dsdata.co.uk:8080/axis/services/SBGGetAirFareQuote?wsdl 
"""


class SBGAirFareQuoteTest(unittest.TestCase):
    """Test case for SBGGetAirFareQuoteService Web service
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

    def test_getAirFareQuote(self):
        request = portType.inputWrapper('getAirFareQuote')
        request._in0 = service.ns1.AirFareQuoteRequest_Def()
        dateTime = time.gmtime(time.time()+864000)
        request._in0._outwardDate = dateTime
        dateTime = time.gmtime(time.time()+5*864000)
        request._in0._returnDate = dateTime
        request._in0._originAirport = 'SFO'
        request._in0._destinationAirport = 'CMH'
        response = portType.getAirFareQuote(request)
        print ResultsToStr(response)

    def test_getAirlines(self):
        request = portType.inputWrapper('getAirlines')
        response = portType.getAirlines(request)
        testdiff.failUnlessEqual(ResultsToStr(response))
    

def makeTestSuite():
    global service, portType, testdiff

    testdiff = None
    kw = {}
    setUp = utils.TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'SBGGetAirFareQuoteService')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = setUp.setService(SBGAirFareQuoteTest, serviceLoc,
                           'SBGGetAirFareQuoteService', 'SBGGetAirFareQuote',
                           **kw)
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(SBGAirFareQuoteTest, 'test_'))
    return suite


def tearDown():
    """Global tear down."""
    testdiff.close()


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
