#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

from SOAPpy import SOAP

ident = '$Id$'

SoapEndpointURL		= 'http://www.alanbushtrust.org.uk/soap/compositions.asp'
MethodNamespaceURI 	= 'urn:alanbushtrust-org-uk:soap.methods'
SoapAction		= MethodNamespaceURI + ".GetCategories"

server = SOAP.SOAPProxy( SoapEndpointURL, namespace=MethodNamespaceURI, soapaction=SoapAction )
for category in server.GetCategories():
   print category
