#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

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

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not XMethodsQueryTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            XMethodsQueryTest.service, XMethodsQueryTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = XMethodsQueryTest.portType


    def test_getAllServiceNames(self):
        request = self.portType.inputWrapper('getAllServiceNames')
        self.handleResponse(self.portType.getAllServiceNames,request)   

    def test_getAllServiceSummaries(self):
        request = self.portType.inputWrapper('getAllServiceSummaries')
        self.handleResponse(self.portType.getAllServiceSummaries,request)   

    def test_getServiceDetail(self):
        request = self.portType.inputWrapper('getServiceDetail')
        request._id = 'uuid:A29C0D6C-5529-0D27-A91A-8E02D343532B'
        self.handleResponse(self.portType.getServiceDetail,request)   
    
    def test_getServiceNamesByPublisher(self):
        request = self.portType.inputWrapper('getServiceNamesByPublisher')
        request._publisherID = 'xmethods.net'
        self.handleResponse(self.portType.getServiceNamesByPublisher,request)   
    
    def notest_getServiceSummariesByPublisher(self):
        request = self.portType.inputWrapper('getServiceSummariesByPublisher')
        request._publisherID = 'xmethods.net'
        self.handleResponse(self.portType.getServiceSummariesByPublisher,request)   


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
