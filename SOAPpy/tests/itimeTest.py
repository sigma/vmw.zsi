#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

from SOAPpy import SOAP

SoapEndpointURL		= 'http://www.lemurlabs.com/rpcrouter'
MethodNamespaceURI 	= 'urn:lemurlabs-ITimeService'

server = SOAP.SOAPProxy(SoapEndpointURL, namespace = MethodNamespaceURI,
    encoding = None)
print server.getInternetTime()
