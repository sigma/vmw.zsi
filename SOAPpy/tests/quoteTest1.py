#!/usr/bin/env python

import sys

sys.path.insert (1, '..')

from SOAPpy import SOAP

ident = '$Id$'

# http://www.durrios.com/Finance.wsdl

server = SOAP.SOAPProxy('http://www.durrios.com/soap/finance.cgi',
    namespace = 'http://www.durrios.com/Finance')

symbol='SUNW'
print symbol, "-> close ", server.stockquote_lasttrade(symbol=symbol), \
   " volume ", server.stockquote_volume(symbol=symbol)
