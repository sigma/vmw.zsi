#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

import SOAP

ident = '$Id$'

server = SOAP.SOAPProxy("http://soap.4s4c.com/whois/soap.asp",
    namespace = "http://www.pocketsoap.com/whois")

print "whois>>", server.whois(name = "actzero.com")
