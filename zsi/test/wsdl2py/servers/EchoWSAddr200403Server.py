#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import sys
from ZSI.ServiceContainer import AsServer
from EchoWSAddr200403Server_server import EchoWSAddr200403Server as EchoServer

"""
EchoServer example service

WSDL:  ../../samples/Echo/Echo.wsdl

"""

class WSAService(EchoServer):
    def wsa_Echo(self, ps, addr):
        response = EchoServer.wsa_Echo(self, ps, addr)
        response.EchoResult = self.request.EchoIn
        return response


if __name__ == "__main__" :
    port = int(sys.argv[1])
    AsServer(port, (WSAService('test'),))
