#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite

"""
Unittest for contacting the XMethodsQuery Web service.

WSDL:  http://www.xmethods.net/wsdl/query.wsdl
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'XMethodsQuery'
PORT_NAME = 'XMethodsQuerySoapPortType'


class XMethodsQueryTest(ServiceTestCase):
    """Test case for XMethodsQuery Web service
    """
    name = "test_XMethodsQuery"
    
    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
        
    def test_getAllServiceNames(self):
        operationName = 'getAllServiceNames'
        request = self.getInputMessageInstance(operationName)
        response = self.RPC(operationName, request)   

    def test_getAllServiceSummaries(self):
        operationName = 'getAllServiceSummaries'
        request = self.getInputMessageInstance(operationName)
        response = self.RPC(operationName, request)
          
    def test_getServiceDetail(self):
        operationName = 'getServiceDetail'
        request = self.getInputMessageInstance(operationName)
        request._id = 'uuid:A29C0D6C-5529-0D27-A91A-8E02D343532B'
        response = self.RPC(operationName, request)   
    
    def test_getServiceNamesByPublisher(self):
        operationName = 'getServiceNamesByPublisher'
        request = self.getInputMessageInstance(operationName)
        request._publisherID = 'xmethods.net'
        response = self.RPC(operationName, request)   
    
    def test_getServiceSummariesByPublisher(self):
        operationName = 'getServiceSummariesByPublisher'
        request = self.getInputMessageInstance(operationName)
        request._publisherID = 'xmethods.net'
        response = self.RPC(operationName, request)  


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
