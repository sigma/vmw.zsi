#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

from SOAPpy import SOAP

ident = '$Id$'

SoapEndpointURL	= 'http://services.xmethods.net/soap/servlet/rpcrouter'
MethodNamespaceURI = 'urn:xmethods-Temperature'

# Do it inline ala SOAP::LITE, also specify the actually ns

server = SOAP.SOAPProxy(SoapEndpointURL)
print "inline", server._ns('ns1', MethodNamespaceURI).getTemp(zipcode='94063')
