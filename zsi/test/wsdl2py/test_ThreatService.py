#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite


"""
Unittest for contacting the threatService Web service.

WSDL:  http://www.boyzoid.com/threat.cfc?wsdl
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'threatService'

PORT_NAME = 'threat'


class threatServiceTest(ServiceTestCase):
    """Test case for threatService Web service
    """
    name = "test_ThreatService"

    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
        
    def test_threatLevel(self):
        operationName = 'threatLevel'
        request = self.getInputMessageInstance(operationName)
        response = self.RPC(operationName, request)
        



def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(threatServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
