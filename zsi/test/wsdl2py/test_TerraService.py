#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
import os
from ZSI import EvaluateException, FaultException

import utils
from paramWrapper import ParamWrapper
from clientGenerator import ClientGenerator

"""
Unittest for contacting the TerraService Web service.

WSDL:  http://terraservice.net/TerraService.asmx?WSDL
"""


class TerraServiceTest(unittest.TestCase):
    """Test case for TerraService Web service
    """

    def setUp(self):
        global testdiff
        global TerraServiceSoap
        
        #kw = {'tracefile': sys.stdout}
        kw = {}
        TerraServiceSoap = service.TerraServiceLocator().getTerraServiceSoap(**kw)

        if not testdiff:
            testdiff = utils.TestDiff(self, 'generatedCode')
            if deleteFile:
                testdiff.deleteFile('TerraService.diffs')
            testdiff.setDiffFile('TerraService.diffs')


    def test_ConvertPlaceToLonLatPt(self):
        request = service.ConvertPlaceToLonLatPtSoapInWrapper()
        request._place = service.ns1.Place_Def()
        request._place._City = 'Oak Harbor'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        response = TerraServiceSoap.ConvertPlaceToLonLatPt(request)   
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_ConvertPlaceToLonLatPt_x1(self):
        request = service.ConvertPlaceToLonLatPtSoapInWrapper()
        request._place = service.ns1.Place_Def()
        request._place._City = 1
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        self.failUnlessRaises(Exception, TerraServiceSoap.ConvertPlaceToLonLatPt, request)

    def test_ConvertLonLatPtToNearestPlace(self):
        request = service.ConvertLonLatPtToNearestPlaceSoapInWrapper()
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        response = TerraServiceSoap.ConvertLonLatPtToNearestPlace(request)   
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def later_ConvertLonLatPtToNearestPlace_x1(self):
        request = service.ConvertLonLatPtToNearestPlaceSoapInWrapper()
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = '-122.64'
        request._point._Lat = 48.29
        response = TerraServiceSoap.ConvertLonLatPtToNearestPlace(request)   
        self.failUnlessRaises(Exception, TerraServiceSoap.ConvertLonLatPtToNearestPlace, request)
    
    def test_ConvertLonLatPtToUtmPt(self):
        request = service.ConvertLonLatPtToUtmPtSoapInWrapper()
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        response = TerraServiceSoap.ConvertLonLatPtToUtmPt(request)  
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def test_ConvertUtmPtToLonLatPt(self):
        request = service.ConvertUtmPtToLonLatPtSoapInWrapper()
        request._utm = service.ns1.UtmPt_Def()
        request._utm._X =  526703.512403
        request._utm._Y =  5348595.96493
        request._utm._Zone =  10
        response = TerraServiceSoap.ConvertUtmPtToLonLatPt(request)  
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_CountPlacesInRect(self):
        request = service.CountPlacesInRectSoapInWrapper()
        request._upperleft = service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -122.64
        request._upperleft._Lat = 48.29
        request._lowerright = service.ns1.LonLatPt_Def()
        request._lowerright._Lon = request._upperleft._Lon + 1.0
        request._lowerright._Lat = request._upperleft._Lon - 1.0
        request._ptype = "HillMountain"
        response = TerraServiceSoap.CountPlacesInRect(request)
        testdiff.failUnlessEqual(ParamWrapper(response))
    
    def later_CountPlacesInRect_x1(self):
        request = service.CountPlacesInRectSoapInWrapper()
        request._upperleft = service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -122.64
        request._upperleft._Lat = 48.29
        request._ptype = "HillMountain"
        response = TerraServiceSoap.CountPlacesInRect(request)
        self.failUnlessRaises(Exception, TerraServiceSoap.CountPlacesInRect, request)
    
    def test_GetAreaFromPt(self):
        request = service.GetAreaFromPtSoapInWrapper()
        request._center = service.ns1.LonLatPt_Def()
        request._center._Lon = -122.64
        request._center._Lat = 48.29
        request._theme = 'Topo'
        request._scale = "Scale2m"
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        response = TerraServiceSoap.GetAreaFromPt(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

        '''TerraService no longer likes these parameters'''
    def badparams_GetAreaFromRect(self):
        request = service.GetAreaFromRectSoapInWrapper()
        request._upperLeft = service.ns1.LonLatPt_Def()
        request._upperLeft._Lon = -122.64
        request._upperLeft._Lat = 48.29
        request._lowerRight = service.ns1.LonLatPt_Def()
        request._lowerRight._Lon = request._upperLeft._Lon + 1.0
        request._lowerRight._Lat = request._upperLeft._Lat - 1.0
        request._theme = 'Topo'
        request._scale = "Scale2m"
        response = TerraServiceSoap.GetAreaFromRect(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetAreaFromTileId(self):
        request = service.GetAreaFromTileIdSoapInWrapper()
        id = service.ns1.TileId_Def()
        id._Theme = 'Topo'
        id._Scale = "Scale2m"
        id._Scene = 8
        id._X = 20
        id._y = 20
        request._id = id
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        response = TerraServiceSoap.GetAreaFromTileId(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetLatLonMetrics(self):
        request = service.GetLatLonMetricsSoapInWrapper()
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        response = TerraServiceSoap.GetLatLonMetrics(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

        # derived type (enum) problem
    def later_GetPlaceFacts(self):
        request = service.GetPlaceFactsSoapInWrapper()
        request._place = service.ns1.Place_Def()
        request._place._City = 'Seattle'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        response = TerraServiceSoap.GetPlaceFacts(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

        # derived type (enum) problem
        # also consistent timeout problem for this call
    def later_GetPlaceList(self):
        request = service.GetPlaceListSoapInWrapper()
        request._placeName = 'New York'
        request._MaxItems = 5
        request._imagePresence = 0
        #response = TerraServiceSoap.GetPlaceList(request)
        #testdiff.failUnlessEqual(ParamWrapper(response))
        self.failUnlessRaises(EvaluateException, TerraServiceSoap.GetPlaceList, request)

    def test_GetPlaceListInRect(self):
        request = service.GetPlaceListInRectSoapInWrapper()
        request._upperleft = service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -123.0
        request._upperleft._Lat = 44.0
        request._lowerright = service.ns1.LonLatPt_Def()
            # needs to be small, otherwise different items
            # returned each time
        request._lowerright._Lon = -122.5
        request._lowerright._Lat = 43.5
        request._ptype = "HillMountain"
        request._MaxItems = 3
        response = TerraServiceSoap.GetPlaceListInRect(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetTheme(self):
        request = service.GetThemeSoapInWrapper()
        request._theme = 'Topo'
        response = TerraServiceSoap.GetTheme(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetTile(self):
        request = service.GetTileSoapInWrapper()
        request._id = service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        response = TerraServiceSoap.GetTile(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetTileMetaFromLonLatPt(self):
        request = service.GetTileMetaFromLonLatPtSoapInWrapper()
        request._theme = 'Topo'
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        request._scale = "Scale4m"
        response = TerraServiceSoap.GetTileMetaFromLonLatPt(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

    def test_GetTileMetaFromTileId(self):
        request = service.GetTileMetaFromTileIdSoapInWrapper()
        request._id = service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        response = TerraServiceSoap.GetTileMetaFromTileId(request)
        testdiff.failUnlessEqual(ParamWrapper(response))

def setUp():
    global testdiff
    global deleteFile
    global service

    deleteFile = utils.handleExtraArgs(sys.argv[1:])
    testdiff = None
    service = ClientGenerator().getModule('config.txt', 'complex_types',
                                          'TerraService', 'generatedCode')
    return service


def makeTestSuite():
    suite = unittest.TestSuite()
    if service:
       suite.addTest(unittest.makeSuite(TerraServiceTest, 'test_'))
    return suite


def main():
    if setUp():
        utils.TestProgram(defaultTest="makeTestSuite")
                  

if __name__ == "__main__" : main()
