#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys

sys.path.insert (1, '..')

from SOAPpy import SOAP

ident = '$Id$'

server = SOAP.SOAPProxy("http://services.xmethods.com:80/perl/soaplite.cgi")
babel = server._ns('urn:xmethodsBabelFish#BabelFish')

print babel.BabelFish(translationmode = "en_fr",
    sourcedata = "The quick brown fox did something or other")
