#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

import SOAP

ident = '$Id$'

SoapEndpointURL		= 'http://www.lemurlabs.com/rpcrouter'
MethodNamespaceURI 	= 'urn:lemurlabs-Fortune'

server = SOAP.SOAPProxy(SoapEndpointURL, namespace = MethodNamespaceURI,
    encoding = None)
print server.getAnyFortune()
