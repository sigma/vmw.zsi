#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

"""
Unittest for contacting the FreeDB Web service.

WSDL:  http://soap.systinet.net:6080/FreeDB/
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'com_systinet_demo_freedb_FreeDBService'
PORT_NAME = 'FreeDBService'


class FreeDBServiceTest(ServiceTestCase):
    """Test case for FreeDBService Web service
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not FreeDBServiceTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            FreeDBServiceTest.service, FreeDBServiceTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = FreeDBServiceTest.portType

    def test_getDetails(self):
        request = self.portType.inputWrapper('getDetails')
        request._title = 'Hollywood Town Hall'
        request._discId = '8509ff0a'
        request._artist = 'Jayhawks'
        request._category = 'rock'
        self.handleResponse(self.portType.getDetails, request)

    def notest_search(self):
        self.handleResponse(self.portType.search, 'Ted Nugent and the Amboy Dukes')

    def notest_searchByTitle(self):
        self.handleResponse(self.portType.searchByTitle, 'Ummagumma')

    def test_searchByTrack(self):
        self.handleResponse(self.portType.searchByTrack, 'Species of Animals')

    def notest_searchByArtist(self):
        self.handleResponse(self.portType.searchByArtist, 'Steppenwolf')
    

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FreeDBServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")

