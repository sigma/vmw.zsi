#!/usr/bin/env python

import sys

sys.path.insert (1, '..')

import SOAP

ident = '$Id$'

# http://www.mybubble.com:8080/mybubbleEntServer/MyBubbleSoapServices.wsdl

server = SOAP.SOAPProxy('http://www.mybubble.com:8080/soap/servlet/rpcrouter',
                        namespace='urn:MyBubble-SoapServices',
                        config=SOAP.SOAPConfig(argsOrdering={"login":("userName", "authenticationToken")}))

symbol='SUNW'
loginToken=server.login(userName='wsguest', authenticationToken='pass')
print server.getServiceResponse(loginToken=loginToken, serviceName="StockQuote", inputText=symbol)
server.logout(logintoken=loginToken)
