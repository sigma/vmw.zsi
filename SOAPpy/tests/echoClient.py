#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys
sys.path.insert(1, "..")

from SOAPpy import *

# Uncomment to see outgoing HTTP headers and SOAP and incoming 
Config.debug = 1

Config.BuildWithNoType = 1
Config.BuildWithNoNamespacePrefix = 1

if len(sys.argv) > 1 and sys.argv[1] == '-s':
    server = SOAPProxy("https://localhost:9900")
else:
    server = SOAPProxy("http://localhost:9900")

# Echo...

# ...in an object
print server.echo_ino("moo")

# ...in an object in an object
print server.prop.echo2("moo")

# ...with keyword arguments 
print server.echo_wkw(third = "three", first = "one", second = "two")

# ...with a context object
print server.echo_wc("moo")

# ...with a header
hd = headerType(data = {"mystring": "Hello World"})
print server._hd(hd).echo_wc("moo")
