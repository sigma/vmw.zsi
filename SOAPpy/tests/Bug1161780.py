#!/usr/bin/env python
import sys
sys.path = ["/home/tim/SOAPpy-0.12.0"] \
            + sys.path
from SOAPpy.Parser import parseSOAPRPC
bad = """<?xml version="1.0"?>
<SOAP-ENV:Envelope
 SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
 xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
	<SOAP-ENV:Body>
		<doSingleRecord SOAP-ENC:root="1">
		</doSingleRecord>
	</SOAP-ENV:Body>
	<ErrorString>The CustomerID tag could not be found or the number contained in the tag was invalid</ErrorString></SOAP-ENV:Envelope>

"""
parseSOAPRPC(bad, attrs = 1)
