#! /usr/bin/env python
# $Header$
'''ZSI:  Zolera Soap Infrastructure.

Copyright 2001, Zolera Systems, Inc.  All Rights Reserved.
'''

_copyright = """ZSI:  Zolera Soap Infrastructure.

Copyright 2001, Zolera Systems, Inc.  All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or
sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, provided that the above copyright notice(s) and
this permission notice appear in all copies of the Software and that
both the above copyright notice(s) and this permission notice appear in
supporting documentation.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF THIRD PARTY RIGHTS. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS
INCLUDED IN THIS NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT
OR CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE
OR PERFORMANCE OF THIS SOFTWARE.

Except as contained in this notice, the name of a copyright holder
shall not be used in advertising or otherwise to promote the sale, use
or other dealings in this Software without prior written authorization
of the copyright holder.
"""

##
##  Stuff imported from elsewhere.
from xml.dom import Node as _Node
try:
    from xml.ns import SOAP as _SOAP, SCHEMA as _SCHEMA
except:
    from ZSI.compat import SOAP as _SOAP, SCHEMA as _SCHEMA
import types as _types

##
##  Public constants.
ZSI_SCHEMA_URI = 'http://www.zolera.com/schemas/ZSI/'


##
##  Not public constants.
_inttypes = [ _types.IntType, _types.LongType ]
_floattypes = [ _types.FloatType ]
_seqtypes = [ _types.TupleType, _types.ListType ]
_stringtypes = [ _types.StringType, _types.UnicodeType ]

##
##  Low-level DOM oriented utilities; useful for typecode implementors.
_attrs = lambda E: E.attributes or []
_children = lambda E: E.childNodes or []
_child_elements = lambda E: [ n for n in (E.childNodes or [])
			if n.nodeType == _Node.ELEMENT_NODE ]

_find_arraytype = lambda E: E.getAttributeNS(_SOAP.ENC, "arrayType")
_find_encstyle = lambda E: E.getAttributeNS(_SOAP.ENV, "encodingStyle")
_find_attr = lambda E, attr: \
		E.getAttributeNS(None, attr) or E.getAttributeNS("", attr)
_find_href = lambda E: _find_attr(E, "href")
_find_xsi_attr = lambda E, attr: \
		E.getAttributeNS(_SCHEMA.XSI3, attr) \
		or E.getAttributeNS(_SCHEMA.XSI1, attr) \
		or E.getAttributeNS(_SCHEMA.XSI2, attr)
_find_type = lambda E: _find_xsi_attr(E, "type")

_textprotect = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
_textunprotect = lambda s: s.replace('&lt;', '<').replace('&amp;', '&')

def _valid_encoding(elt):
    '''Does this node have a valid encoding?
    '''
    enc = _find_encstyle(elt) or None
    if enc in [ None, _SOAP.ENC ]: return 1
    for e in enc.split():
	if e.startswith(_SOAP.ENC):
	    # XXX Is this correct?  Once we find a Sec5 compatible
	    # XXX encoding, should we check that all the rest are from
	    # XXX that same base?  Perhaps.  But since the "if enc in"
	    # XXX test will surely get 99% of the cases, leave it for now.
	    return 1
    return 0

def _backtrace(elt, dom):
    '''Return a "backtrace" from the given element to the DOM root,
    in XPath syntax.
    '''
    s = ''
    while elt != dom:
	name, parent = elt.nodeName, elt.parentNode
	if parent == None: break
	matches = [ c for c in _child_elements(parent) 
			if c.nodeName == name ]
	if len(matches) == 1:
	    s = '/' + name + s
	else:
	    i = matches.index(elt) + 1
	    s = ('/%s[%d]' % (name, i)) + s
	elt = parent
    return s


##
##  Exception classes.
class ParseException(Exception):
    '''Exception raised during parsing.
    '''

    def __init__(self, str, inheader, elt=None, dom=None):
	Exception.__init__(self)
	self.str, self.inheader, self.trace = str, inheader, None
	if elt and dom:
	    self.trace = _backtrace(elt, dom)

    def __str__(self):
	if self.trace:
	    return self.str + '\n[Element trace: ' + self.trace + ']'
	return self.str

    def __repr__(self):
	return "<%s.ParseException at 0x%x>" % (__name__, id(self))


class EvaluateException(Exception):
    '''Exception raised during data evaluation (serialization).
    '''

    def __init__(self, str, trace=None):
	Exception.__init__(self)
	self.str, self.trace = str, trace

    def __str__(self):
	if self.trace:
	    return self.str + '\n[Element trace: ' + self.trace + ']'
	return self.str

    def __repr__(self):
	return "<%s.EvaluateException at 0x%x>" % (__name__, id(self))


##
##  Importing the rest of ZSI.
import version
def Version():
    return version.Version

from writer import SoapWriter
from parse import ParsedSoap
from fault import Fault, \
    FaultFromActor, FaultFromException, FaultFromFaultMessage, \
    FaultFromNotUnderstood, FaultFromZSIException
import TC
TC.RegisterType(TC.Void)
TC.RegisterType(TC.String)
TC.RegisterType(TC.URI)
TC.RegisterType(TC.Base64String)
TC.RegisterType(TC.HexBinaryString)
TC.RegisterType(TC.Integer)
TC.RegisterType(TC.Decimal)
TC.RegisterType(TC.Boolean)
TC.RegisterType(TC.Duration)
TC.RegisterType(TC.gDateTime)
TC.RegisterType(TC.gDate)
TC.RegisterType(TC.gYearMonth)
TC.RegisterType(TC.gYear)
TC.RegisterType(TC.gMonthDay)
TC.RegisterType(TC.gDay)
TC.RegisterType(TC.gTime)
TC.RegisterType(TC.Apache.Map)
TC.RegisterType(TC.Apache.SOAPStruct)

if __name__ == '__main__': print _copyright
