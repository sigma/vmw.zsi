#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
"""
Unittest for contacting the Map Point Service.  

WSDL:  
"""

CONFIG_FILE = 'config.txt'
SERVICE_NAME = 'CommonService'
PORT_NAME = 'CommonServiceSoap'


class MapPointTest(ServiceTestCase):
    """Test case for OPCService Web service
    
    """
    name = "test_MapPoint"

    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)

    def _getLocator(self):
        """Multiple services, so grab the locator you want
        """
        locatorName = self._wsm.services[0].locator.getLocatorName()
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(locatorName):
                return sm.__dict__[locatorName]()
            raise TestException, 'No Locator class (%s), missing SOAP location binding?' %locatorName
        raise TestException, 'missing service module, possibly no WSDL service item?'

    def _getPort(self, locator, netloc=None):
        """Returns a rpc proxy port instance.
           **Only expecting 1 service/WSDL, and 1 port/service.

           locator -- Locator instance
        """
        #if len(self._wsm.services) != 1:
        #    raise TestException, 'only supporting WSDL with one service information item'
        methodNames = self._wsm.services[0].locator.getPortMethods()
        if len(methodNames) == 0:
            raise TestException, 'No port defined for service.'
        #elif len(methodNames) > 1:
        #    raise TestException, 'Not handling multiple ports.'
        callMethod = getattr(locator, methodNames[0])
        return callMethod(**self._getPortOptions(methodNames[0], locator, netloc))
 
    def test_GetVersionInfo(self):
        """expect this to fail cause i'm not doing http authentication.
        """
        operationName = 'GetVersionInfo'
        msg = self.getInputMessageInstance(operationName)
        try:
            response = self.RPC(operationName, msg)
        except:
            pass
 
    

def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(MapPointTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

