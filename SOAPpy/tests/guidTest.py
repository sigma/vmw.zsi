#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

import SOAP

ident = '$Id$'

# Three ways to do namespaces, force it at the server level
server = SOAP.SOAPProxy("http://www.itfinity.net:8008/soap/guid/default.asp",
		namespace="http://www.itfinity.net/soap/guid/guid.xsd")
print "GUID>>", server.NextGUID()
