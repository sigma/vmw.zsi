#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException

from utils import TestSetUp, TestProgram, failureException
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
        try:
            response = portType.getDetails(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)


    def test_search(self):
        try:
            response = portType.search('Ted Nugent and the Amboy Dukes')
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)


    def test_searchByTitle(self):
        try:
            response = portType.searchByTitle('Ummagumma')
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)


    def test_searchByTrack(self):
        try:
            response = portType.searchByTrack('Species of Animals')
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)


    def test_searchByArtist(self):
        try:
            response = portType.searchByArtist('Steppenwolf')
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    

def makeTestSuite():
    global service, portType

    kw = {}
    setUp = TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types',
                           'com.systinet.demo.freedb.FreeDBService')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType =  setUp.setService(FreeDBServiceTest, serviceLoc,
                    'com.systinet.demo.freedb.FreeDBService', 'FreeDBService',
                    **kw)
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(FreeDBServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")

