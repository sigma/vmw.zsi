#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys
from ZSI.ServiceContainer import AsServer
from EchoServer_server import EchoServer

"""
EchoServer example service

WSDL:  ../../samples/Echo/Echo.wsdl

"""


class Service(EchoServer):
    def soap_Echo(self, ps):
        request,response = EchoServer.soap_Echo(self, ps)
        response.EchoResult = request.EchoIn
        return request,response


if __name__ == "__main__" :
    port = int(sys.argv[1])
    AsServer(port, (Service('test'),))
