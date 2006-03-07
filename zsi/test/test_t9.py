#!/usr/bin/env python
import unittest, sys, sha, base64
from ZSI import _get_element_nsuri_name
from ZSI.parse import ParsedSoap
from ZSI.wstools.c14n import Canonicalize
from ZSI.wstools.Namespaces import WSA200403
from cStringIO import StringIO


class CanonicalizeFromTestCase(unittest.TestCase):
    "c14n tests, this has nothing to do with ws-addressing."

    def setUp(self):
        self.ps = ParsedSoap(SOAP)
        self.el = filter(lambda el: _get_element_nsuri_name(el) == (WSA200403.ADDRESS, "From"), 
                      self.ps.header_elements)[0]

    def tearDown(self):
        del self.ps
        del self.el

    def check_c14n(self):
        """http://www.w3.org/TR/xml-c14n
        """
        s = StringIO()
        Canonicalize(self.el, s, unsuppressedPrefixes=None)
        cxml = s.getvalue()
        d1 = base64.encodestring(sha.sha(C14N_INC1).digest()).strip()
        d2 = base64.encodestring(sha.sha(cxml).digest()).strip()
        self.assertEqual(d1, d2)
        self.assertEqual(d1, C14N_INC1_DIGEST)

    def check_c14n_exc(self):
        """http://www.w3.org/TR/xml-exc-c14n/
        """
        s = StringIO()
        Canonicalize(self.el, s, unsuppressedPrefixes=[])
        cxml = s.getvalue()
        d1 = base64.encodestring(sha.sha(C14N_EXCL1).digest()).strip()
        d2 = base64.encodestring(sha.sha(cxml).digest()).strip()
        self.assertEqual(d1, C14N_EXCL1_DIGEST)
        self.assertEqual(d1, d2)

    def check_c14n_exc_unsuppressed(self):
        """http://www.w3.org/TR/xml-exc-c14n/
        The method of canonicalization described in this specification receives 
        an InclusiveNamespaces PrefixList parameter, which lists namespace prefixes 
        that are handled in the manner described by the Canonical XML Recommendation 
        """
        s = StringIO()
        Canonicalize(self.el, s, unsuppressedPrefixes=['xsi', 'xsd'])
        cxml = s.getvalue()
        d1 = base64.encodestring(sha.sha(C14N_EXCL2).digest()).strip()
        d2 = base64.encodestring(sha.sha(cxml).digest()).strip()
        self.assertEqual(d1, C14N_EXCL2_DIGEST)
        self.assertEqual(d1, d2)


def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CanonicalizeFromTestCase, "check"))
    return suite


C14N_EXCL1_DIGEST =  "xSOXT+dlQwo5uT9PbK08of6W9PM="
C14N_EXCL1 = """<wsa:From xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" ns3:Id="id-7680063" soapenv:mustUnderstand="0"><wsa:Address>http://bosshog.lbl.gov:9999/wsrf/services/SecureCounterService</wsa:Address><wsa:ReferenceProperties><ns1:CounterKey xmlns:ns1="http://counter.com" ns3:Id="10112">10577413</ns1:CounterKey></wsa:ReferenceProperties></wsa:From>"""

C14N_INC1_DIGEST =  "qdU4f7/+BeHV/JlVGIPM90fNeV8="
C14N_INC1 = """<wsa:From xmlns:ns1="http://counter.com" xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ns3:Id="id-7680063" soapenv:mustUnderstand="0"><wsa:Address>http://bosshog.lbl.gov:9999/wsrf/services/SecureCounterService</wsa:Address><wsa:ReferenceProperties><ns1:CounterKey ns3:Id="10112">10577413</ns1:CounterKey></wsa:ReferenceProperties></wsa:From>"""

C14N_EXCL2_DIGEST = "+IEqF6DRo36Bh93A06S7C4Cmcuo="
C14N_EXCL2 = """<wsa:From xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ns3:Id="id-7680063" soapenv:mustUnderstand="0"><wsa:Address>http://bosshog.lbl.gov:9999/wsrf/services/SecureCounterService</wsa:Address><wsa:ReferenceProperties><ns1:CounterKey xmlns:ns1="http://counter.com" ns3:Id="10112">10577413</ns1:CounterKey></wsa:ReferenceProperties></wsa:From>"""


SOAP = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/03/addressing" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><soapenv:Header>
	<wsse:Security soapenv:mustUnderstand="1" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
	<ds:SignedInfo>
	<ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="soapenv wsa xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:CanonicalizationMethod>
	<ds:SignatureMethod Algorithm="http://www.globus.org/2002/04/xmlenc#gssapi-sign"/>
	<ds:Reference URI="#id-8409752">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="wsa xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>m9pihAqIBdcdk7ytDvccj89eWi8=</ds:DigestValue>
	</ds:Reference>
	<ds:Reference URI="#id-11434871">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>ofD+Ket5kzR2u/5jWKbFTMtmigk=</ds:DigestValue>
	</ds:Reference>
	<ds:Reference URI="#id-19645447">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>SoQ7RlJa3r94weDWBuWAg/BvydQ=</ds:DigestValue>
	</ds:Reference>
	<ds:Reference URI="#id-5428820">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>z6sCEkkRJrCuY/C0S5b+46WfyMs=</ds:DigestValue>
	</ds:Reference>
	<ds:Reference URI="#id-7680063">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>+IEqF6DRo36Bh93A06S7C4Cmcuo=</ds:DigestValue>
	</ds:Reference>
	<ds:Reference URI="#id-28476580">
	<ds:Transforms>
	<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces PrefixList="xsd xsi" xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#"/></ds:Transform>
	</ds:Transforms>
	<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
	<ds:DigestValue>NFltkKAJpmMkPbJQj5MW1qVceto=</ds:DigestValue>
	</ds:Reference>
	</ds:SignedInfo>
	<ds:SignatureValue>AAAAAAAAAAMAAAvZTrXlZjRSO7tP12tId+lehprEKgk=</ds:SignatureValue>
	<ds:KeyInfo>
	<wsse:SecurityTokenReference><wsse:Reference URI="#SecurityContextToken-32970611" ValueType="http://www.globus.org/ws/2004/09/security/sc#GSSAPI_CONTEXT_TOKEN"/></wsse:SecurityTokenReference>
	</ds:KeyInfo>
	</ds:Signature><wsc:SecurityContextToken wsu:Id="SecurityContextToken-32970611" xmlns:wsc="http://schemas.xmlsoap.org/ws/2004/04/sc" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><wsc:Identifier>3b1ef410-ab3d-11da-9436-88b687faed94</wsc:Identifier></wsc:SecurityContextToken></wsse:Security><wsa:MessageID wsu:Id="id-11434871" soapenv:mustUnderstand="0" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">uuid:3d592ca0-ab3d-11da-9436-88b687faed94</wsa:MessageID><wsa:To wsu:Id="id-19645447" soapenv:mustUnderstand="0" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">http://schemas.xmlsoap.org/ws/2004/03/addressing/role/anonymous</wsa:To><wsa:Action wsu:Id="id-5428820" soapenv:mustUnderstand="0" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">http://counter.com/CounterPortType/addResponse</wsa:Action><wsa:From ns3:Id="id-7680063" soapenv:mustUnderstand="0" xmlns:ns1="http://counter.com" xmlns:ns3="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><wsa:Address>http://bosshog.lbl.gov:9999/wsrf/services/SecureCounterService</wsa:Address><wsa:ReferenceProperties><ns1:CounterKey ns3:Id="10112">10577413</ns1:CounterKey></wsa:ReferenceProperties></wsa:From><wsa:RelatesTo RelationshipType="wsa:Reply" wsu:Id="id-28476580" soapenv:mustUnderstand="0" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">uuid:1141449047.05</wsa:RelatesTo></soapenv:Header><soapenv:Body wsu:Id="id-8409752" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><addResponse xmlns="http://counter.com">13</addResponse></soapenv:Body></soapenv:Envelope>"""


def main():
    unittest.main(defaultTest="makeTestSuite")

if __name__ == '__main__': 
    main()
