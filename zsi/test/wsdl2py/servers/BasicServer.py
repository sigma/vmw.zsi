#!/usr/bin/env python

import sys
from ZSI.ServiceContainer import AsServer
from BasicServer_server import BasicServer

"""
BasicServer example service

WSDL:  BasicComm.wsdl

"""


class Service(BasicServer):
    def soap_Basic(self, ps):
        response = BasicServer.soap_Basic(self, ps)
        response._BasicResult = self.request._BasicIn
        return response

    def soap_BasicOneWay(self, ps):
        response = BasicServer.soap_BasicOneWay(self, ps)
        if self.request._BasicIn == 'fault':
            # return a soap:fault
            raise RuntimeError, 'you wanted a fault?'

        return response


if __name__ == "__main__" :
    port = int(sys.argv[1])
    AsServer(port, (Service('test'),))
