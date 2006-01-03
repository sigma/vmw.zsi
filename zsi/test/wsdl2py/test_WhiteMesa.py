#!/usr/bin/env python

############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite, TestException

"""
Unittest for contacting the WhiteMesa web service for rpc/literal tests.

WSDL: http://www.whitemesa.net/wsdl/test-rpc-lit.wsdl

"""

CONFIG_FILE = 'config.txt'
CONFIG_SECTION = 'WSDL'
SERVICE_NAME = 'WhiteMesa'
PORT_NAME = 'Soap11TestRpcLitPort'


class WhiteMesaTest(ServiceTestCase):
    """Test case for ZipCodeResolver Web service
    """
    name = "test_WhiteMesa"

    def getInputMessageInstance(self, operationName):
        """Returns an instance of the input message to send for this operation.
        Grap the SOAP 1.1 port.
           operationName -- WSDL port operation name
        """
        service = self._wsm._wsdl.services[0]
        port = service.ports[1]
        try:
            self._checkPort(port, operationName)
        except TestException, ex:
            raise TestException('Service(%s)' %service.name, *ex.args)

        for operation in port.getBinding().getPortType().operations:
            if operation.name == operationName:
                break
        else:
            raise TestException, 'Missing operation (%s) in portType operations'  %operationName

        inputMsgName = '%s' %operation.input.message[1]
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(inputMsgName):
                inputMsgWrapper = sm.__dict__[inputMsgName]()
                return inputMsgWrapper
            else:
                raise TestException, 'service missing input message (%s)' %(inputMsgName)

        raise TestException, 'port(%s) does not define operation %s' \
            %(port.name, operationName)

    def setUp(self):
        self._portName = PORT_NAME
        ServiceTestCase.setSection(self,self.name)
        ServiceTestCase.setUp(self)

    def test_EchoBoolean(self):
        operationName = 'echoBoolean'
        request = self.getInputMessageInstance(operationName)
        request._inputBoolean = True
        response = self.RPC(operationName, request)


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(WhiteMesaTest, 'test_'))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")
