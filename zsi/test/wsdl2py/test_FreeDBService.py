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
Unittest for contacting the FreeDB Web service.

WSDL:  http://soap.systinet.net:6080/FreeDB/
"""

class FreeDBServiceTest(unittest.TestCase):
    """Test case for FreeDBService Web service
    """

    def test_getDetails(self):
        request = portType.inputWrapper('getDetails')
        request._title = 'Hollywood Town Hall'
        request._discId = '8509ff0a'
        request._artist = 'Jayhawks'
        request._category = 'rock'
        response = portType.getDetails(request)
        print ResultsToStr(response)

    def test_search(self):
        response = portType.search('Ted Nugent and the Amboy Dukes')
        print ResultsToStr(response)

    def test_searchByTitle(self):
        response = portType.searchByTitle('Ummagumma')
        print ResultsToStr(response)

    def test_searchByTrack(self):
        response = portType.searchByTrack('Species of Animals')
        print ResultsToStr(response)

    def test_searchByArtist(self):
        response = portType.searchByArtist('Steppenwolf')
        print ResultsToStr(response)
    

def makeTestSuite():
    global service, portType

    service, portType =  utils.testSetUp(FreeDBServiceTest,
                    'com.systinet.demo.freedb.FreeDBService', 'FreeDBService')
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(FreeDBServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")

