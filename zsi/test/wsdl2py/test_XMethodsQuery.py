#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import EvaluateException

import utils
from paramWrapper import ResultsToStr
from clientGenerator import ClientGenerator

"""
Unittest for contacting the XMethodsQuery Web service.

WSDL:  http://www.xmethods.net/wsdl/query.wsdl
"""


class XMethodsQueryTest(unittest.TestCase):
    """Test case for XMethodsQuery Web service
    """

    def setUp(self):
        """unittest calls setUp and tearDown after each
           test method call.
        """
        global testdiff
        global XMethodsPort

        kw = {}
        #kw = {'tracefile': sys.stdout}
        XMethodsPort = service.XMethodsQueryLocator().getXMethodsQuerySoapPortType(**kw)
        if not testdiff:
            testdiff = utils.TestDiff(self, 'diffs')
            testdiff.setDiffFile('XMethodsQuery.diffs')


    def test_getAllServiceNames(self):
        request = service.getAllServiceNames2SoapInWrapper()
        response = XMethodsPort.getAllServiceNames(request)   
        print ResultsToStr(response)

    def test_getAllServiceSummaries(self):
        request = service.getAllServiceSummaries1SoapInWrapper()
        response = XMethodsPort.getAllServiceSummaries(request)   
        print ResultsToStr(response)

    def test_getServiceDetail(self):
        request = service.getServiceDetail4SoapInWrapper()
        request._id = 'uuid:A29C0D6C-5529-0D27-A91A-8E02D343532B'
        response = XMethodsPort.getServiceDetail(request)   
        print ResultsToStr(response)
    
    def test_getServiceNamesByPublisher(self):
        request = service.getServiceNamesByPublisher3SoapInWrapper()
        request._publisherID = 'xmethods.net'
        response = XMethodsPort.getServiceNamesByPublisher(request)   
        print ResultsToStr(response)
    
    def test_getServiceSummariesByPublisher(self):
        request = service.getServiceSummariesByPublisher0SoapInWrapper()
        request._publisherID = 'xmethods.net'
        response = XMethodsPort.getServiceSummariesByPublisher(request)   
        print ResultsToStr(response)


def setUp():
    global testdiff
    global deleteFile
    global service

    deleteFile = utils.handleExtraArgs(sys.argv[1:])
    testdiff = None
    service = ClientGenerator().getModule('config.txt', 'complex_types',
                                          'XMethodsQuery', 'generatedCode')
    return service



def makeTestSuite():
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(XMethodsQueryTest, 'test_'))
    return suite


def main():
    if setUp():
        utils.TestProgram(defaultTest="makeTestSuite")
                  

if __name__ == "__main__" : main()
