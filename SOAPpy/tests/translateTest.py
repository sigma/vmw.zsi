#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.
ident = '$Id$'

import os, re
import sys
sys.path.insert(1, "..")

from SOAPpy import *

# Check for a web proxy definition in environment
try:
   proxy_url=os.environ['http_proxy']
   phost, pport = re.search('http://([^:]+):([0-9]+)', proxy_url).group(1,2)
   proxy = "%s:%s" % (phost, pport)
except:
   proxy = None


if 1:

   server = WSDL.Proxy('http://www.webservicex.com/TranslateService.asmx?WSDL',
                       http_proxy=proxy,
                       ns="http://www.webservicex.com/")
   
   print server.show_methods()

   server.soapproxy.config.dumpHeadersOut = True
   server.soapproxy.config.dumpSOAPOut = True

   server.soapproxy.config.dumpSOAPIn = True
   server.soapproxy.config.dumpHeadersIn = True



else:

   server = SOAPProxy("http://www.webservicex.net/TranslateService.asmx/",
                      http_proxy=proxy,
                      soapaction="http://www.webservicex.net/Translate")
   
   server.config.dumpHeadersOut = True
   server.config.dumpSOAPOut = True
   
   server.config.dumpSOAPIn = True
   server.config.dumpHeadersIn = True

query = server.Translate(LanguageMode="EnglishToFrench",
                         Text="Hello, how are you today?")

print query

print repr(query)
