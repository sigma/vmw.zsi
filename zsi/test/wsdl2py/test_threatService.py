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
Unittest for contacting the threatService Web service.

WSDL:  http://www.boyzoid.com/threat.cfc?wsdl
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'threatService'
PORT_NAME = 'threat'


class threatServiceTest(utils.ServiceTestCase):
    """Test case for threatService Web service
    """
    
    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not threatServiceTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            threatServiceTest.service, threatServiceTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = threatServiceTest.portType

    def test_threatLevel(self):
        request = self.portType.inputWrapper('threatLevel')
        response = self.portType.threatLevel(request)
        print ResultsToStr(response)


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(threatServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
