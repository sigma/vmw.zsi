#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

import SOAP

ident = '$Id$'

# Three ways to do namespaces, force it at the server level

server = SOAP.SOAPProxy("http://services.xmethods.com:80/soap",
    namespace = 'urn:xmethods-delayed-quotes')

print "IBM>>", server.getQuote(symbol = 'IBM')

# Do it inline ala SOAP::LITE, also specify the actually ns

server = SOAP.SOAPProxy("http://services.xmethods.com:80/soap")
print "IBM>>", server._ns('ns1',
    'urn:xmethods-delayed-quotes').getQuote(symbol = 'IBM')

# Create a namespaced version of your server

dq = server._ns('urn:xmethods-delayed-quotes')
print "IBM>>", dq.getQuote(symbol='IBM')
print "ORCL>>", dq.getQuote(symbol='ORCL')
print "INTC>>", dq.getQuote(symbol='INTC')
