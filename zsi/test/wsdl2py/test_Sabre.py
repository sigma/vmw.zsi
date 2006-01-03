#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
"""
Unittest for contacting 

WSDL:  http://webservices.sabre.com/wsdl/sabreXML1.0.00/res/SessionCreateRQ.wsdl
"""

CONFIG_FILE = 'config.txt'
SERVICE_NAME = 'SessionCreateRQService'
PORT_NAME = 'SessionCreatePortType'


class ServiceTest(ServiceTestCase):
    """Test case for Sabre Web service
    
    """
    name = "test_Sabre"

    def setUp(self):
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)
        
    def test_SessionCreate(self):
        """
_________________________________ Mon Jan  2 13:41:22 2006 REQUEST:
<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="http://www.opentravel.org/OTA/2002/11"><ns1:SessionCreateRQ><ns1:POS><ns1:Source PseudoCityCode="SF"></ns1:Source></ns1:POS></ns1:SessionCreateRQ></SOAP-ENV:Body></SOAP-ENV:Envelope>
_________________________________ Mon Jan  2 13:41:22 2006 RESPONSE:
Server: Netscape-Enterprise/6.0
Date: Mon, 02 Jan 2006 21:41:21 GMT
Content-length: 1568
Content-type: text/xml; charset="utf-8"
Soapaction: ""

<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Header><wsse:Security xmlns:wsse="http://schemas.xmlsoap.org/ws/2002/12/secext"/></soap-env:Header><soap-env:Body><soap-env:Fault><faultcode>soap-env:Client.ConversationIdRequired</faultcode><faultstring>Conversation id required</faultstring><detail><StackTrace>com.sabre.universalservices.base.session.SessionException: errors.session.USG_CONVERSATION_ID_REQUIRED
        at com.sabre.universalservices.gateway.control.SecurityInterceptor.executeOnRequest(SecurityInterceptor.java:111)
        at com.sabre.universalservices.base.interceptor.Interceptor.execute(Interceptor.java:113)
        at com.sabre.universalservices.base.interceptor.InterceptorChain.applyInterceptors(InterceptorChain.java:32)
        at com.sabre.universalservices.base.interceptor.InterceptorManager.process(InterceptorManager.java:116)
        at com.sabre.universalservices.gateway.control.WSGateway.onMessage(WSGateway.java:297)
        at com.sabre.universalservices.gateway.control.WSGateway.handleRequest(WSGateway.java:208)
        at com.sabre.universalservices.gateway.control.WSGateway.doPost(WSGateway.java:156)
        at javax.servlet.http.HttpServlet.service(HttpServlet.java:760)
        at javax.servlet.http.HttpServlet.service(HttpServlet.java:853)
        at com.iplanet.server.http.servlet.NSServletRunner.invokeServletService(NSServletRunner.java:919)
        at com.iplanet.server.http.servlet.NSServletRunner.Service(NSServletRunner.java:483)
</StackTrace></detail></soap-env:Fault></soap-env:Body></soap-env:Envelope>
E
        """
        operationName = 'SessionCreateRQ'

        msg = self.getInputMessageInstance(operationName)
        msg.POS = msg.new_POS()
        msg.POS.Source = msg.POS.new_Source()
        msg.POS.Source.set_attribute_PseudoCityCode("SF") 

        self.failUnlessRaises(FaultException, self._ports[0].SessionCreateRQ, msg)
        #response = self._ports[0].SessionCreateRQ(msg)
        #response.Success
        #response.Warnings
        #response.ConversationId 
        #response.Errors
        

def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(ServiceTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

