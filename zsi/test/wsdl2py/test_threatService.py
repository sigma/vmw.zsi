#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ZSI import FaultException
import utils
from paramWrapper import ResultsToStr
from clientGenerator import ClientGenerator

"""
Unittest for contacting the threatService Web service.

WSDL:  http://www.boyzoid.com/threat.cfc?wsdl
"""


class threatServiceTest(unittest.TestCase):
    """Test case for threatService Web service
    """

    
    def test_threatLevel(self):
        request = portType.inputWrapper('threatLevel')
        response = portType.threatLevel(request)
        print ResultsToStr(response)


def makeTestSuite():
    global service, portType

    kw = {}
    setUp = utils.TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'threatService')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = setUp.setService(threatServiceTest, serviceLoc,
                                'threatService', 'threat',
                                **kw)

    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(threatServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
