#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest

from utils import ServiceTestCase, TestProgram

"""
Unittest for contacting the TerraService Web service.

WSDL:  http://terraservice.net/TerraService.asmx?WSDL
"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'complex_types'
SERVICE_NAME = 'TerraService'
PORT_NAME = 'TerraServiceSoap'


class TerraServiceTest(ServiceTestCase):
    """Test case for TerraService Web service
    """

    service = None
    portType = None

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        if not TerraServiceTest.service:
            kw, serviceLoc = self.getConfigOptions(CONFIG_FILE,
                                                CONFIG_SECTION, SERVICE_NAME)
            TerraServiceTest.service, TerraServiceTest.portType = \
                     self.setService(serviceLoc, SERVICE_NAME, PORT_NAME, **kw)
        self.portType = TerraServiceTest.portType
        self.service = TerraServiceTest.service

    def test_ConvertPlaceToLonLatPt(self):
        request = self.portType.inputWrapper('ConvertPlaceToLonLatPt')
        request._place = self.service.ns1.Place_Def()
        request._place._City = 'Oak Harbor'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        self.handleResponse(self.portType.ConvertPlaceToLonLatPt,request,diff=True)   
    def test_ConvertPlaceToLonLatPt_x1(self):
        request = self.portType.inputWrapper('ConvertPlaceToLonLatPt')
        request._place = self.service.ns1.Place_Def()
        request._place._City = 1
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        try:
            self.failUnlessRaises(Exception, self.portType.ConvertPlaceToLonLatPt, request)
        except FaultException, msg:
            if failureException(FaultException, msg):
                raise

    def notest_ConvertLonLatPtToNearestPlace(self):
        request = self.portType.inputWrapper('ConvertLonLatPtToNearestPlace')
        request._point = self.service.ns1.LonLatPt_Def()
        request._point._Lon = -122.643
        request._point._Lat = 48.297
        self.handleResponse(self.portType.ConvertLonLatPtToNearestPlace,request,diff=True)   
    
    def notest_ConvertLonLatPtToUtmPt(self):
        request = self.portType.inputWrapper('ConvertLonLatPtToUtmPt')
        request._point = self.service.ns1.LonLatPt_Def()
        request._point._Lon = -122.643
        request._point._Lat = 48.297
        self.handleResponse(self.portType.ConvertLonLatPtToUtmPt,request,diff=True)  
    def notest_ConvertUtmPtToLonLatPt(self):
        request = self.portType.inputWrapper('ConvertUtmPtToLonLatPt')
        request._utm = self.service.ns1.UtmPt_Def()
        request._utm._X =  526703.512403
        request._utm._Y =  5348595.96493
        request._utm._Zone =  10
        self.handleResponse(self.portType.ConvertUtmPtToLonLatPt,request,diff=True)  
    def test_CountPlacesInRect(self):
        request = self.portType.inputWrapper('CountPlacesInRect')
        request._upperleft = self.service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -122.647
        request._upperleft._Lat = 48.293
        request._lowerright = self.service.ns1.LonLatPt_Def()
        request._lowerright._Lon = request._upperleft._Lon + 1.0
        request._lowerright._Lat = request._upperleft._Lon - 1.0
        request._ptype = "HillMountain"
        self.handleResponse(self.portType.CountPlacesInRect,request,diff=True)
    
    def test_GetAreaFromPt(self):
        request = self.portType.inputWrapper('GetAreaFromPt')
        request._center = self.service.ns1.LonLatPt_Def()
        request._center._Lon = -122.647
        request._center._Lat = 48.293
        request._theme = 'Topo'
        request._scale = "Scale2m"
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        self.handleResponse(self.portType.GetAreaFromPt,request,diff=True)

    def test_GetAreaFromRect(self):
        request = self.portType.inputWrapper('GetAreaFromRect')
        request._upperLeft = self.service.ns1.LonLatPt_Def()
        request._upperLeft._Lon = -122.647
        request._upperLeft._Lat = 48.293
        request._lowerRight = self.service.ns1.LonLatPt_Def()
        request._lowerRight._Lon = request._upperLeft._Lon + 1.0
        request._lowerRight._Lat = request._upperLeft._Lat - 1.0
        request._theme = 'Topo'
        request._scale = "Scale2m"
        self.handleResponse(self.portType.GetAreaFromRect,request,diff=True)

    def test_GetAreaFromTileId(self):
        request = self.portType.inputWrapper('GetAreaFromTileId')
        id = self.service.ns1.TileId_Def()
        id._Theme = 'Topo'
        id._Scale = "Scale2m"
        id._Scene = 8
        id._X = 20
        id._y = 20
        request._id = id
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        self.handleResponse(self.portType.GetAreaFromTileId,request,diff=True)

    def test_GetLatLonMetrics(self):
        request = self.portType.inputWrapper('GetLatLonMetrics')
        request._point = self.service.ns1.LonLatPt_Def()
        request._point._Lon = -122.647
        request._point._Lat = 48.293
        self.handleResponse(self.portType.GetLatLonMetrics,request,diff=True)

        # derived type (enum) problem
        # skipping it for now
    def error_GetPlaceFacts(self):
        request = self.portType.inputWrapper('GetPlaceFacts')
        request._place = self.service.ns1.Place_Def()
        request._place._City = 'Seattle'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        self.handleResponse(self.portType.GetPlaceFacts,request,diff=True)

        # derived type (enum) problem
        # also inconsistent timeout problem for this call
    def error_GetPlaceList(self):
        request = self.portType.inputWrapper('GetPlaceList')
        request._placeName = 'New York'
        request._MaxItems = 5
        request._imagePresence = 0
        self.handleResponse(self.portType.GetPlaceList,request,diff=True)

        # inconsistent timeout problem for this call
    def test_GetPlaceListInRect(self):
        request = self.portType.inputWrapper('GetPlaceListInRect')
        request._upperleft = self.service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -123.0
        request._upperleft._Lat = 44.0
        request._lowerright = self.service.ns1.LonLatPt_Def()
            # needs to be small, otherwise different items
            # returned each time
        request._lowerright._Lon = -122.8
        request._lowerright._Lat = 43.8
        request._ptype = "HillMountain"
        request._MaxItems = 3
        self.handleResponse(self.portType.GetPlaceListInRect,request,diff=True)

    def test_GetTheme(self):
        request = self.portType.inputWrapper('GetTheme')
        request._theme = 'Topo'
        self.handleResponse(self.portType.GetTheme,request,diff=True)

    def test_GetTile(self):
        request = self.portType.inputWrapper('GetTile')
        request._id = self.service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        self.handleResponse(self.portType.GetTile,request,diff=True)

    def test_GetTileMetaFromLonLatPt(self):
        request = self.portType.inputWrapper('GetTileMetaFromLonLatPt')
        request._theme = 'Topo'
        request._point = self.service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        request._scale = "Scale4m"
        self.handleResponse(self.portType.GetTileMetaFromLonLatPt,request,diff=True)

    def test_GetTileMetaFromTileId(self):
        request = self.portType.inputWrapper('GetTileMetaFromTileId')
        request._id = self.service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        self.handleResponse(self.portType.GetTileMetaFromTileId,request,diff=True)

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TerraServiceTest, 'test_'))
    return suite


if __name__ == "__main__" :
    TestProgram(defaultTest="makeTestSuite")
