#!/usr/bin/env python

############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite

"""
Unittest for contacting the Amazon Web service.

WSDL:  http://soap.amazon.com/schemas/AmazonWebServices.wsdl

"""

class AmazonServiceTest(ServiceTestCase):
    """Test case for AmazonService Web service.  
    To write a new service just define a method 'test' and retrieve an input message 
    instance via the operation name, fill in the request, and call the RPC method.
    Then you can test the response.

    name -- module name, also used to index service in configuration file.
    test_section -- section test is categorized in, do runtime checking
          to make sure test belongs in this section.

    """
    name = "test_AmazonWebService"
    
    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
    
    def testAuthorSearchRequest(self):
        operationName = "AuthorSearchRequest"
        request = self.getInputMessageInstance(operationName)
        #Set up the request
        request._AuthorSearchRequest._author = 'shakespeare'
        request._AuthorSearchRequest._page = '1'
        request._AuthorSearchRequest._mode = 'books'
        request._AuthorSearchRequest._tag = 'webservices-20'
        request._AuthorSearchRequest._type = 'lite'
        request._AuthorSearchRequest._devtag = 'your-dev-tag'
        request._AuthorSearchRequest._format = 'xml'
        request._AuthorSearchRequest._version = '1.0'
        #Test the return message
        response = self.RPC(operationName, request)

def makeTestSuite():
    """makeTestSuite
    """
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AmazonServiceTest, 'test'))
    return suite

if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

