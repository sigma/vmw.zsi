#! /usr/bin/env python
IN='''<SOAP-ENV:Envelope
 xmlns="http://www.example.com/schemas/TEST"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:ZSI="http://www.zolera.com/schemas/ZSI/">
<SOAP-ENV:Body>
<hreftest>
    <xmltest href="http://www.zolera.com/schemas/zsi.xsd"/>
    <stringtest href="http://www.microsoft.com"/>
</hreftest>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'''

from ZSI import *
from ZSI import resolvers
import sys
OUT = sys.stdout

try:
    r = resolvers.NetworkResolver(['http:'])
    ps = ParsedSoap(IN, resolver=r.Resolve)
except ParseException, e:
    FaultFromZSIException(e).AsSOAP(OUT)
    sys.exit(1)
except Exception, e:
    # Faulted while processing; assume it's in the header.
    FaultFromException(e, 1, sys.exc_info()[2]).AsSOAP(OUT)
    sys.exit(1)

print 'resolving'
typecode = TC.Struct(None, [
                TC.XML('xmltest'),
                TC.String('stringtest', resolver=r.Opaque),
            ])
try:
    dict = ps.Parse(typecode)
#except EvaluateException, e:
#    FaultFromZSIException(e).AsSOAP(OUT)
#    sys.exit(1)
except Exception, e:
    # Faulted while processing; now it's the body
    FaultFromException(e, 0, sys.exc_info()[2]).AsSOAP(OUT)
    sys.exit(1)

from xml.dom.ext import PrettyPrint
PrettyPrint(dict['xmltest'])
print '**', dict['stringtest'], '**'
