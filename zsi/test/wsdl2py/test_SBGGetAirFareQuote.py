#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
import time

from ZSI import FaultException

from utils import TestSetUp, TestProgram, TestDiff, failureException
from paramWrapper import ResultsToStr

"""
Unittest for contacting the SBGGetAirFareQuoteService Web service.

WSDL: http://wavendon.dsdata.co.uk:8080/axis/services/SBGGetAirFareQuote?wsdl 
"""


class SBGAirFareQuoteTest(unittest.TestCase):
    """Test case for SBGGetAirFareQuoteService Web service
    """

    def test_getAirFareQuote(self):
        request = portType.inputWrapper('getAirFareQuote')
        request._in0 = service.ns1.AirFareQuoteRequest_Def()
        dateTime = time.gmtime(time.time()+864000)
        request._in0._outwardDate = dateTime
        dateTime = time.gmtime(time.time()+5*864000)
        request._in0._returnDate = dateTime
        request._in0._originAirport = 'SFO'
        request._in0._destinationAirport = 'CMH'
        try:
            response = portType.getAirFareQuote(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)


    def test_getAirlines(self):
        request = portType.inputWrapper('getAirlines')
        try:
            response = portType.getAirlines(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            TestDiff(self).failUnlessEqual(ResultsToStr(response))
    

def makeTestSuite():
    global service, portType

    kw = {}
    setUp = TestSetUp('config.txt')
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


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
