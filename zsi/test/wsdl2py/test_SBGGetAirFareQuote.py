#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
import time
from ZSI import EvaluateException

import utils
from paramWrapper import ParamWrapper
from clientGenerator import ClientGenerator

"""
Unittest for contacting the SBGGetAirFareQuoteService Web service.

WSDL: http://wavendon.dsdata.co.uk:8080/axis/services/SBGGetAirFareQuote?wsdl 
"""


class SBGGetAirFareQuoteServiceTest(unittest.TestCase):
    """Test case for SBGGetAirFareQuoteService Web service
    """

    def setUp(self):
        """unittest calls setUp and tearDown after each
           test method call.
        """
        global testdiff
        global SBGAirFareQuote

        if not testdiff:
            testdiff = utils.TestDiff(self, 'generatedCode')
            testdiff.setDiffFile('SBGGetAirFareQuoteService.diffs')
          
        kw = {}
        #kw = { 'tracefile' : sys.stdout }
        SBGAirFareQuote = service.SBGGetAirFareQuoteServiceLocator().getSBGGetAirFareQuote(**kw)

    
    def test_getAirFareQuote(self):
        request = service.getAirFareQuoteRequestWrapper()
        request._in0 = service.ns1.AirFareQuoteRequest_Def()
        dateTime = time.gmtime(time.time()+864000)
        request._in0._outwardDate = dateTime
        dateTime = time.gmtime(time.time()+5*864000)
        request._in0._returnDate = dateTime
        request._in0._originAirport = 'SFO'
        request._in0._destinationAirport = 'CMH'
        response = SBGAirFareQuote.getAirFareQuote(request)
        print ParamWrapper(response)

    def test_getAirlines(self):
        request = service.getAirlinesRequestWrapper()
        response = SBGAirFareQuote.getAirlines(request)
        testdiff.failUnlessEqual(ParamWrapper(response))
    

def setUp():
    global testdiff
    global deleteFile
    global service

    deleteFile = utils.handleExtraArgs(sys.argv[1:])
    testdiff = None
    service = ClientGenerator().getModule('config.txt', 'complex_types',
                                   'SBGGetAirFareQuoteService',
                                   'generatedCode')
    return service


def makeTestSuite():
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(SBGGetAirFareQuoteServiceTest, 'test_'))
    return suite


def main():
    if setUp():
        utils.TestProgram(defaultTest="makeTestSuite")
                  

if __name__ == "__main__" : main()
