#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

import SOAP

if SOAP.Config.SSLserver:
    from M2Crypto import SSL

# Simple echo
def echo(s):
    return s + s

# An echo class
class echoBuilder2:
    def echo2(self, val):
        return val * 3

# A class that has an instance variable which is an echo class
class echoBuilder:
    def __init__(self):
        self.prop = echoBuilder2()

    def echo_ino(self, val):
        return val + val

# Echo with context
def echo_wc(s, _SOAPContext):
    c = _SOAPContext

    sep = '-' * 72

    # The Context object has extra info about the call

    print "-- XML", sep[7:]
    print c.xmldata     # The original XML request

    print "-- Header", sep[10:]
    print c.header      # The SOAP Header or None if not present

    if c.header:
        print "-- Header.mystring", sep[19:]
        print c.header.mystring         # An element of the SOAP Header

    print "-- Body", sep[8:]
    print c.body        # The whole Body object

    print "-- Peer", sep[8:]
    print c.connection.getpeername()    # The socket object, useful for

    print "-- SOAPAction", sep[14:]
    print c.soapaction                  # The SOAPaction HTTP header

    print "-- HTTP headers", sep[16:]
    print c.httpheaders                 # All the HTTP headers

    return s + s

# Echo with keyword arguments
def echo_wkw(**kw):
    return kw['first'] + kw['second'] + kw['third']

if len(sys.argv) > 1 and sys.argv[1] == '-s':
    if not SOAP.Config.SSLserver:
        raise RuntimeError, \
            "this Python installation doesn't have OpenSSL and M2Crypto"
    ssl_context = SSL.Context()
    ssl_context.load_cert('validate/server.pem')
else:
    ssl_context = None

server = SOAP.SOAPServer(('localhost',9900), ssl_context = ssl_context)

server.registerFunction(echo)

# Register a whole object
o = echoBuilder()
server.registerObject(o)

# Register a function which gets called with the Context object
server.registerFunction(SOAP.MethodSig(echo_wc, keywords = 0, context = 1))

# Register a function that takes keywords
server.registerKWFunction(echo_wkw)

# Start the server
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
