#! /usr/bin/env python

try:
    3 / 0
except Exception, e:
    a = e

from ZSI import *

f = FaultFromException(e, 0)
text = f.AsSOAP()
i = 0
for l in text.split('\n'):
    print i, l
    i += 1
ps = ParsedSoap(text)
if ps.IsAFault():
    f = FaultFromFaultMessage(ps)
    print f.AsSOAP()
