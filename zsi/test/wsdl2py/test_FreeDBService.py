#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
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
    name = "test_FreeDBService"
    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
        
    def test_getDetails(self):
        """
        Request is a CDInfo
        """
        operationName = 'getDetails'
        request = self.getInputMessageInstance(operationName)
        request._title = 'Hollywood Town Hall'
        request._discId = '8509ff0a'
        request._artist = 'Jayhawks'
        request._category = 'rock'
        response = self.RPC(operationName, request)    

    def test_search(self):
        """
        Request is a string for this operation
        """
        operationName = "search"
        searchString = "Ted Nugent and the Amboy Dukes"
        response = self.RPC(operationName, searchString)

    def test_searchByTitle(self):
        """
        Request is a string for this operation
        """
        operationName = "searchByTitle"
        searchString = 'Ummagumma'
        response = self.RPC(operationName, searchString)

    def test_searchByTrack(self):
        """
        Request is a string for this operation
        """
        operationName = "searchByTrack"
        searchString = "Species of Animals"
        response = self.RPC(operationName, searchString)

    def test_searchByArtist(self):
        """
        Request is a string for this operation
        """
        operationName = "searchByArtist"
        searchString = "SteppenWolf"
        response = self.RPC(operationName, searchString)
    

def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(FreeDBServiceTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

