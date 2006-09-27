#!/usr/bin/env python

############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import main, ServiceTestCase, ServiceTestSuite, TestException

"""
Unittest for contacting the Amazon ECommerce Service

WSDL: 

"""
# General targets
def dispatch():
    """Run all dispatch tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AmazonTestCase, 'test_dispatch'))
    return suite

def local():
    """Run all local tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AmazonTestCase, 'test_local'))
    return suite

def net():
    """Run all network tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AmazonTestCase, 'test_net'))
    return suite
    
def all():
    """Run all tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AmazonTestCase, 'test_'))
    return suite


class AmazonTestCase(ServiceTestCase):
    """Test case for ZipCodeResolver Web service
    """
    name = "test_AWSECommerceService"
    client_file_name = "AWSECommerceService_services.py"
    types_file_name  = "AWSECommerceService_services_types.py"
    server_file_name = "AWSECommerceService_services_server.py"

    def __init__(self, methodName):
        ServiceTestCase.__init__(self, methodName)
        self.wsdl2py_args.append('-b')
        self.wsdl2py_args.append('--lazy')
    
    def test_net_ItemSearch(self):
        loc = self.client_module.AWSECommerceServiceLocator()
        port = loc.getAWSECommerceServicePortType(**self.getPortKWArgs())

        msg = self.client_module.ItemSearchRequestMsg()
        msg.SubscriptionId = '0HP1WHME000749APYWR2'
        request = msg.new_Request()
        msg.Request = [request]

        # request
        request.ItemPage = 1
        request.SearchIndex = "Books"
        request.Keywords = 'Tamerlane'
        request.ResponseGroup = ['Medium',]

        response = port.ItemSearch(msg)

        response.OperationRequest
        self.failUnless(response.OperationRequest.Errors is None, 'ecommerce site reported errors')

        response.OperationRequest.Arguments
        for i in response.OperationRequest.Arguments.Argument: 
             i.get_attribute_Name()
             i.get_attribute_Value()

        for i in response.OperationRequest.HTTPHeaders.Header or []:
             i.get_attribute_Name()
             i.get_attribute_Value()
             
        response.OperationRequest.RequestId
        response.OperationRequest.RequestProcessingTime
        for its in response.Items:
            for it in its.Item:
                it.ASIN; 
                it.Accessories; 
                it.AlternateVersions; 
                it.BrowseNodes
                it.Collections; it.CustomerReviews ;it.DetailPageURL
                it.EditorialReviews; it.Errors; it.ImageSets; it.ItemAttributes
                it.LargeImage; it.ListmaniaLists; it.MediumImage; it.MerchantItemAttributes
                it.OfferSummary; it.Offers; it.ParentASIN; it.SalesRank; it.SearchInside
                it.SimilarProducts; it.SmallImage; it.Subjects; it.Tracks;
                it.VariationSummary; it.Variations


if __name__ == "__main__" :
    main()
