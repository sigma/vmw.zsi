#!/usr/bin/env python

############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
import os

from ZSI import EvaluateException, FaultException
import utils
from paramWrapper import ResultsToStr

"""
Unittest for contacting the TerraService Web service.

WSDL:  http://terraservice.net/TerraService.asmx?WSDL
"""


class TerraServiceSoapTest(unittest.TestCase):
    """Test case for TerraService Web service
    """

    def setUp(self):
        """Done this way because unittest instantiates a TestCase
           for each test method, but want all diffs to go in one
           file.  Not doing testdiff as a global this way causes
           problems.
        """
        global testdiff

        if not testdiff:
            testdiff = utils.TestDiff(self, 'diffs')

    def test_ConvertPlaceToLonLatPt(self):
        request = portType.inputWrapper('ConvertPlaceToLonLatPt')
        request._place = service.ns1.Place_Def()
        request._place._City = 'Oak Harbor'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        try:
            response = portType.ConvertPlaceToLonLatPt(request)   
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    def test_ConvertPlaceToLonLatPt_x1(self):
        request = portType.inputWrapper('ConvertPlaceToLonLatPt')
        request._place = service.ns1.Place_Def()
        request._place._City = 1
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        try:
            self.failUnlessRaises(Exception, portType.ConvertPlaceToLonLatPt, request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise

    def test_ConvertLonLatPtToNearestPlace(self):
        request = portType.inputWrapper('ConvertLonLatPtToNearestPlace')
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.643
        request._point._Lat = 48.297
        try:
            response = portType.ConvertLonLatPtToNearestPlace(request)   
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    
    def test_ConvertLonLatPtToUtmPt(self):
        request = portType.inputWrapper('ConvertLonLatPtToUtmPt')
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.643
        request._point._Lat = 48.297
        try:
            response = portType.ConvertLonLatPtToUtmPt(request)  
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    
    def test_ConvertUtmPtToLonLatPt(self):
        request = portType.inputWrapper('ConvertUtmPtToLonLatPt')
        request._utm = service.ns1.UtmPt_Def()
        request._utm._X =  526703.512403
        request._utm._Y =  5348595.96493
        request._utm._Zone =  10
        try:
            response = portType.ConvertUtmPtToLonLatPt(request)  
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    def test_CountPlacesInRect(self):
        request = portType.inputWrapper('CountPlacesInRect')
        request._upperleft = service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -122.647
        request._upperleft._Lat = 48.293
        request._lowerright = service.ns1.LonLatPt_Def()
        request._lowerright._Lon = request._upperleft._Lon + 1.0
        request._lowerright._Lat = request._upperleft._Lon - 1.0
        request._ptype = "HillMountain"
        try:
            response = portType.CountPlacesInRect(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    
    def test_GetAreaFromPt(self):
        request = portType.inputWrapper('GetAreaFromPt')
        request._center = service.ns1.LonLatPt_Def()
        request._center._Lon = -122.647
        request._center._Lat = 48.293
        request._theme = 'Topo'
        request._scale = "Scale2m"
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        try:
            response = portType.GetAreaFromPt(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


    def test_GetAreaFromRect(self):
        request = portType.inputWrapper('GetAreaFromRect')
        request._upperLeft = service.ns1.LonLatPt_Def()
        request._upperLeft._Lon = -122.647
        request._upperLeft._Lat = 48.293
        request._lowerRight = service.ns1.LonLatPt_Def()
        request._lowerRight._Lon = request._upperLeft._Lon + 1.0
        request._lowerRight._Lat = request._upperLeft._Lat - 1.0
        request._theme = 'Topo'
        request._scale = "Scale2m"
        try:
            response = portType.GetAreaFromRect(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


    def test_GetAreaFromTileId(self):
        request = portType.inputWrapper('GetAreaFromTileId')
        id = service.ns1.TileId_Def()
        id._Theme = 'Topo'
        id._Scale = "Scale2m"
        id._Scene = 8
        id._X = 20
        id._y = 20
        request._id = id
        request._displayPixWidth = 2
        request._displayPixHeight = 2
        try:
            response = portType.GetAreaFromTileId(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    def test_GetLatLonMetrics(self):
        request = portType.inputWrapper('GetLatLonMetrics')
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.647
        request._point._Lat = 48.293
        try:
            response = portType.GetLatLonMetrics(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


        # derived type (enum) problem, but only sometimes (?)
        # skipping it for now
        
    def b_GetPlaceFacts(self):
        request = portType.inputWrapper('GetPlaceFacts')
        request._place = service.ns1.Place_Def()
        request._place._City = 'Seattle'
        request._place._State = 'Washington'
        request._place._Country = 'United States'
        try:
            response = portType.GetPlaceFacts(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        except EvaluateException:
            pass
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


        # derived type (enum) problem
        # also inconsistent timeout problem for this call
    def test_GetPlaceList(self):
        request = portType.inputWrapper('GetPlaceList')
        request._placeName = 'New York'
        request._MaxItems = 5
        request._imagePresence = 0
        try:
            response = portType.GetPlaceList(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        except EvaluateException:
            pass
        else:
            raise


        # inconsistent timeout problem for this call
    def test_GetPlaceListInRect(self):
        request = portType.inputWrapper('GetPlaceListInRect')
        request._upperleft = service.ns1.LonLatPt_Def()
        request._upperleft._Lon = -123.0
        request._upperleft._Lat = 44.0
        request._lowerright = service.ns1.LonLatPt_Def()
            # needs to be small, otherwise different items
            # returned each time
        request._lowerright._Lon = -122.8
        request._lowerright._Lat = 43.8
        request._ptype = "HillMountain"
        request._MaxItems = 3
        try:
            response = portType.GetPlaceListInRect(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))

    def test_GetTheme(self):
        request = portType.inputWrapper('GetTheme')
        request._theme = 'Topo'
        try:
            response = portType.GetTheme(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


    def test_GetTile(self):
        request = portType.inputWrapper('GetTile')
        request._id = service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        try:
            response = portType.GetTile(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


    def test_GetTileMetaFromLonLatPt(self):
        request = portType.inputWrapper('GetTileMetaFromLonLatPt')
        request._theme = 'Topo'
        request._point = service.ns1.LonLatPt_Def()
        request._point._Lon = -122.64
        request._point._Lat = 48.29
        request._scale = "Scale4m"
        try:
            response = portType.GetTileMetaFromLonLatPt(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


    def test_GetTileMetaFromTileId(self):
        request = portType.inputWrapper('GetTileMetaFromTileId')
        request._id = service.ns1.TileId_Def()
        request._id._Theme = 'Topo'
        request._id._Scale = 'Scale2m'
        request._id._Scene = 8
        request._id._X = 20
        request._id._Y = 20
        try:
            response = portType.GetTileMetaFromTileId(request)
        except FaultException, msg:
            if utils.failureException(FaultException, msg):
                raise
        else:
            testdiff.failUnlessEqual(ResultsToStr(response))


def makeTestSuite():
    global service, portType, testdiff

    testdiff = None
    kw = {}
    setUp = utils.TestSetUp('config.txt')
    serviceLoc = setUp.get('complex_types', 'TerraService')
    useTracefile = setUp.get('configuration', 'tracefile') 
    if useTracefile == '1':
        kw['tracefile'] = sys.stdout
    service, portType = setUp.setService(TerraServiceSoapTest, serviceLoc,
                             'TerraService', 'TerraServiceSoap', **kw)
    suite = unittest.TestSuite()
    if service:
        suite.addTest(unittest.makeSuite(TerraServiceSoapTest, 'test_'))
    return suite

def tearDown():
    """Global tear down."""
    testdiff.close()


if __name__ == "__main__" :
    utils.TestProgram(defaultTest="makeTestSuite")
    tearDown()
