#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

"""
Unittest for contacting services where WSDL specification
has no schema.

TemperatureService

    WSDL:  http://www.xmethods.net/sd/2001/TemperatureService.wsdl

WorldTimeService

    WSDL:  http://ws.digiposs.com/WorldTime.jws?wsdl

"""


CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'no_schemas'

TEMP_SERVICE_NAME = 'TemperatureService'
TEMP_PORT_NAME = 'TemperaturePortType'

WORLD_SERVICE_NAME = 'WorldTimeService'
WORLD_PORT_NAME = 'WorldTime'


class TemperatureServiceTest(ServiceTestCase):
    """Test case for TemperatureService Web service
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not TemperatureServiceTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION,
                                                TEMP_SERVICE_NAME)
            TemperatureServiceTest.service, TemperatureServiceTest.portType = \
                     self.setService(serviceLoc, TEMP_SERVICE_NAME,
                                     TEMP_PORT_NAME, **kw)
        self.portType = TemperatureServiceTest.portType

    def test_getTemp(self):
        request = self.portType.inputWrapper('getTemp')
        request._zipcode = '94720'
        self.handleResponse(self.portType.getTemp,request)
    

class WorldTimeServiceTest(ServiceTestCase):
    """Test case for WorldTimeService Web service
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not WorldTimeServiceTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION,
                                                WORLD_SERVICE_NAME)
            WorldTimeServiceTest.service, WorldTimeServiceTest.portType = \
                     self.setService(serviceLoc, WORLD_SERVICE_NAME,
                                                WORLD_PORT_NAME, **kw)
        self.portType = WorldTimeServiceTest.portType

    def test_tzStampNow(self):
        request = self.portType.inputWrapper('tzStampNow')
        request._tZone = 'Pacific'
        self.handleResponse(self.portType.tzStampNow,request)
    
    def test_utcStampNow(self):
        request = self.portType.inputWrapper('utcStampNow')
        self.handleResponse(self.portType.utcStampNow,request)
    

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TemperatureServiceTest, 'test_'))
    suite.addTest(unittest.makeSuite(WorldTimeServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
