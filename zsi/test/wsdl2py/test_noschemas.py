#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException

from utils import TestSetUp, TestProgram, TestDiff, failureException
from paramWrapper import ResultsToStr

"""
Unittest for contacting services where WSDL specification
has no schema.

TemperatureService

    WSDL:  http://www.xmethods.net/sd/2001/TemperatureService.wsdl

WorldTimeService

    WSDL:  http://ws.digiposs.com/WorldTime.jws?wsdl

"""


class TemperatureServiceTest(unittest.TestCase):
    """Test case for TemperatureService Web service
    """

    def test_getTemp(self):
        request = tempPortType.inputWrapper('getTemp')
        request._zipcode = '94720'
        try:
            response = tempPortType.getTemp(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    

class WorldTimeServiceTest(unittest.TestCase):
    """Test case for WorldTimeService Web service
    """

    def test_tzStampNow(self):
        request = worldTimePortType.inputWrapper('tzStampNow')
        request._tZone = 'Pacific'
        try:
            response = worldTimePortType.tzStampNow(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    
    def test_utcStampNow(self):
        request = worldTimePortType.inputWrapper('utcStampNow')
        try:
            response = worldTimePortType.utcStampNow(request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise
        else:
            print ResultsToStr(response)
    

def makeTestSuite():
    global tempPortType
    global worldTimePortType

    kw = {}

    setUp = TestSetUp('config.txt')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout

    serviceLoc = setUp.get('no_schemas', 'TemperatureService')
    service, tempPortType = setUp.setService(TemperatureServiceTest, serviceLoc,
                                  'TemperatureService', 'TemperaturePortType',
                                  **kw)
    
    serviceLoc = setUp.get('no_schemas', 'WorldTimeService')
    service, worldTimePortType = \
        setUp.setService(WorldTimeServiceTest, serviceLoc,
                                  'WorldTimeService', 'WorldTime',
                                  **kw)

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(TemperatureServiceTest, 'test_'))
        suite.addTest(unittest.makeSuite(WorldTimeServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
