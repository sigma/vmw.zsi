#! /usr/bin/env python
# $Header$
'''General typecodes.
'''

from ZSI import _copyright, _children, _child_elements, \
	_floattypes, _stringtypes, _seqtypes, _find_arraytype, _find_href, \
	_find_encstyle, _textprotect, _textunprotect, \
	_find_xsi_attr, _find_type, \
	EvaluateException, _valid_encoding
from xml.dom import Node
try:
    from xml.dom.ext import Canonicalize
    from xml.ns import SCHEMA, SOAP
except:
    from ZSI.compat import Canonicalize, SCHEMA, SOAP

import re, types

from base64 import decodestring as b64decode, encodestring as b64encode
from urllib import unquote as urldecode, quote as urlencode
from binascii import unhexlify as hexdecode, hexlify as hexencode


_is_xsd_or_soap_ns = lambda ns: ns in [
			SCHEMA.XSD3, SOAP.ENC, SCHEMA.XSD1, SCHEMA.XSD2, ]
_find_nil = lambda E: _find_xsi_attr(E, "null") or _find_xsi_attr(E, "nil")

class TypeCode:
    '''The parent class for all parseable SOAP types.
    Class data:
	typechecks -- do init-time type checking if non-zero
    Class data subclasses may define:
	parselist -- list of valid SOAP types for this class, as
	    (uri,name) tuples, where a uri of None means "all the XML
	    Schema namespaces"
	errorlist -- parselist in a human-readable form; will be
	    generated if/when needed
	seriallist -- list of Python types or user-defined classes
	    that this typecode can serialize.
    '''

    typechecks = 1

    def __init__(self, pname=None, **kw):
	'''Baseclass initialization.
	Instance data (and usually keyword arg)
	    pname -- the parameter name (localname).
	    nspname -- the namespace for the parameter;
		None to ignore the namespace
	    oname -- output name (could have NS prefix)
	    typed -- output xsi:type attribute
	    repeatable -- element can appear more than once
	    optional -- the item is optional
	    default -- default value
	    unique -- data item is not aliased (no href/id needed)
	'''
	if type(pname) in _seqtypes:
	    self.nspname, self.pname = pname
	else:
	    self.nspname, self.pname = None, pname
	self.oname = kw.get('oname', self.pname)
	if self.pname:
	    i = self.pname.find(':')
	    if i > -1: self.pname = self.pname[i + 1:]

	self.optional = kw.get('optional', 0)
	self.typed = kw.get('typed', 1)
	self.repeatable = kw.get('repeatable', 0)
	self.unique = kw.get('unique', 0)
	if kw.has_key('default'): self.default = kw['default']
	self.resolver = None

    def parse(self, elt, ps):
	'''elt -- the DOM element being parsed
	ps -- the ParsedSoap object.
	'''
	raise EvaluateException("Unimplemented evaluation", ps.Backtrace(elt))

    def SimpleHREF(self, elt, ps, tag):
	'''Simple HREF for non-string and non-struct and non-array.
	'''
	if elt.hasChildNodes(): return elt
	href = _find_href(elt)
	if not href:
	    if self.optional: return None
	    raise EvaluateException('Non-optional ' + tag + ' missing',
		    ps.Backtrace(elt))
	return ps.FindLocalHREF(href, elt, 0)

    def get_parse_and_errorlist(self):
	'''Get the parselist and human-readable version (errorlist, because
	it's used in error messages).
	'''
	d = self.__class__.__dict__
	parselist = d.get('parselist')
	errorlist = d.get('errorlist')
	if parselist and not errorlist:
	    errorlist = []
	    for t in parselist:
		if t[1] not in errorlist: errorlist.append(t[1])
	    errorlist = ' or '.join(errorlist)
	    d['errorlist'] = errorlist
	return (parselist, errorlist)

    def checkname(self, elt, ps):
	'''See if the name and type of the "elt" element is what we're
	looking for.   Return the element's type.
	'''

	parselist,errorlist = self.get_parse_and_errorlist()
	ns, name = elt.namespaceURI, elt.localName

	if ns == SOAP.ENC:
	    # Element is in SOAP namespace, so the name is a type.
	    if parselist and \
	    (None, name) not in parselist and (ns, name) not in parselist:
		raise EvaluateException(
		'Type mismatch (got %s wanted %s) (SOAP encoding namespace)' % \
			(name, errorlist), ps.Backtrace(elt))
	    return (ns, name)

	# Not a type, check name matches.
	if self.nspname and ns != self.nspname:
	    raise EvaluateException('Type NS mismatch (got %s wanted %s)' % \
		(ns, self.nspname), ps.Backtrace(elt))

	if self.pname and name != self.pname:
	    raise EvaluateException('Name mismatch (got %s wanted %s)' % \
		(name, self.pname), ps.Backtrace(elt))
	return self.checktype(elt, ps)

    def checktype(self, elt, ps):
	'''See if the type of the "elt" element is what we're looking for.
	Return the element's type.
	'''
	type = _find_type(elt)
	if type == None or type == "":
	    return (None,None)

	# Parse the QNAME.
	list = type.split(':')
	if len(list) != 2:
	    raise EvaluateException('Malformed type attribute (not two colons)',
		    ps.Backtrace(elt))
	uri = ps.GetElementNSdict(elt).get(list[0])
	if uri == None:
	    raise EvaluateException('Malformed type attribute (bad NS)',
		    ps.Backtrace(elt))
	type = list[1]
	parselist,errorlist = self.get_parse_and_errorlist()
	if not parselist or \
	(uri,type) in parselist or \
	(_is_xsd_or_soap_ns(uri) and (None,type) in parselist):
	    return (uri,type)
	raise EvaluateException(
		'Type mismatch (%s namespace) (got %s wanted %s)' % \
		(uri, type, errorlist), ps.Backtrace(elt))

    def name_match(self, elt):
	'''Simple boolean test to see if we match the element name.
	'''
	return self.pname == elt.localName and \
		    self.nspname in [None, elt.namespaceURI]

    def nilled(self, elt, ps):
	'''Is the element NIL, and is that okay?
	'''
	if _find_nil(elt) not in [ "true",  "1"]: return 0
	if not self.optional:
	    raise EvaluateException('Required element is NIL',
		    ps.Backtrace(elt))
	return 1

    def simple_value(self, elt, ps):
	'''Get the value of the simple content of this element.
	'''
	if not _valid_encoding(elt):
	    raise EvaluateException('Invalid encoding', ps.Backtrace(elt))
	c = _children(elt)
	if len(c) == 0:
	    raise EvaluateException('Value missing', ps.Backtrace(elt))
	for c_elt in c:
	    if c_elt.nodeType == Node.ELEMENT_NODE:
		raise EvaluateException('Sub-elements in value',
		    ps.Backtrace(c_elt))

	# It *seems* to be consensus that ignoring comments and
	# concatenating the text nodes is the right thing to do.
	return ''.join([E.nodeValue for E in c
		if E.nodeType 
		in [ Node.TEXT_NODE, Node.CDATA_SECTION_NODE ]])


class Any(TypeCode):
    '''When the type isn't defined in the schema, but must be specified
    in the incoming operation.
	parsemap -- a type to class mapping (updated by descendants), for
		parsing
	serialmap -- same, for (outgoing) serialization
    '''
    parsemap, serialmap = {}, {}

    def __init__(self, pname=None, **kw):
	TypeCode.__init__(self, pname, **kw)
	self.aslist = kw.get('aslist', 0)
	# If not derived, and optional isn't set, make us optional
	# so that None can be parsed.
	if self.__class__ == Any and not kw.has_key('optional'):
	    self.optional = 1

    def parse_into_dict(self, elt, ps):
	c = _child_elements(elt)
	count = len(c)
	v = {}
	if count == 0:
	    href = _find_href(elt)
	    if not href: return v
	    elt = ps.FindLocalHREF(href, elt)
	    self.checktype(elt, ps)
	    c = _child_elements(elt)
	    count = len(c)
	    if count == 0: return v
	if self.nilled(elt, ps): return None
	for c_elt in c:
	    v[str(c_elt.nodeName)] = self.parse(c_elt, ps)
	return v

    def parse(self, elt, ps):
	(ns,type) = self.checkname(elt, ps)
	if not type and self.nilled(elt, ps): return None
	if not elt.hasChildNodes():
	    href = _find_href(elt)
	    if not href:
		if self.optional: return None
		raise EvaluateException('Non-optional Any missing',
			ps.Backtrace(elt))
	    elt = ps.FindLocalHREF(href, elt)
	    (ns,type) = self.checktype(elt, ps)
	if not type and elt.namespaceURI == SOAP.ENC:
	    ns,type = SOAP.ENC, elt.localName
	if not type or (ns,type) == (SOAP.ENC,'Array'):
	    if self.aslist or _find_arraytype(elt):
		return [ Any(aslist=self.aslist).parse(e, ps)
			    for e in _child_elements(elt) ]
	    if len(_child_elements(elt)) == 0:
		raise EvaluateException("Any cannot parse untyped element",
			ps.Backtrace(elt))
	    return self.parse_into_dict(elt, ps)
	parser = Any.parsemap.get((ns,type))
	if not parser and _is_xsd_or_soap_ns(ns):
	    parser = Any.parsemap.get((None,type))
	if not parser:
	    raise EvaluateException('''Any can't parse element''',
		    ps.Backtrace(elt))
	return parser.parse(elt, ps)

    def serialize(self, sw, pyobj, **kw):
	kw['name'] = self.oname
	n = kw.get('name', 'E%x' % id(pyobj))
	tc = type(pyobj)
	if tc == types.DictType or self.aslist:
	    print >>sw, '<%s>' % n
	    if self.aslist:
		for val in pyobj:
		    Any().serialize(sw, val)
	    else:
		for key,val in pyobj.items():
		    Any(pname=key).serialize(sw, val)
	    print >>sw, '</%s>' % n
	    return
	if tc in _seqtypes:
	    print >>sw, '<%s SOAP-ENC:arrayType="xsd:anyType[%d]">' % \
		(n, len(pyobj))
	    a = Any()
	    for e in pyobj:
		a.serialize(sw, e, name='element')
	    print >>sw, '</%s>' % n
	    return
	if tc == types.InstanceType:
	    tc = pyobj.__class__
	    serializer = Any.serialmap.get(tc)
	    if not serializer:
		tc = (types.ClassType, pyobj.__class__.__name__)
		serializer = Any.serialmap.get(tc)
	else:
	    serializer = Any.serialmap.get(tc)
	if not serializer:
	    # Last-chance; serialize instances as dictionary
	    if type(pyobj) != types.InstanceType:
		raise EvaluateException('''Any can't serialize ''' + \
			repr(pyobj))
	    self.serialize(sw, pyobj.__dict__, **kw)
	else:
	    serializer.serialize(sw, pyobj, **kw)


def RegisterType(C, clobber=0, *args, **keywords):
    instance = apply(C, args, keywords)
    for t in C.__dict__.get('parselist', []):
	prev = Any.parsemap.get(t)
	if prev:
	    if prev.__class__ == C: continue
	    if not clobber:
		raise TypeError(
		    str(C) + ' duplicating parse registration for ' + str(t))
	Any.parsemap[t] = instance
    for t in C.__dict__.get('seriallist', []):
	ti = type(t)
	if ti in [ types.TypeType, types.ClassType]:
	    key = t
	elif ti in _stringtypes:
	    key = (types.ClassType, t)
	else:
	    raise TypeError(str(t) + ' is not a class name')
	prev = Any.serialmap.get(key)
	if prev:
	    if prev.__class__ == C: continue
	    if not clobber:
		raise TypeError(
		    str(C) + ' duplicating serial registration for ' + str(t))
	Any.serialmap[key] = instance


class Void(TypeCode):
    '''A null type.
    '''
    parselist = [ (None,'nil') ]
    seriallist = [ types.NoneType ]

    def parse(self, elt, ps):
	self.checkname(elt, ps)
	if elt.hasChildNodes():
	    raise EvaluateException('Void got a value', ps.Backtrace(elt))
	return None

    def serialize(self, sw, pyobj, **kw):
	n = kw.get('name', self.oname) or ('E%x' % id(pyobj))
	print >>sw, '''<%s%s xsi:nil="1"/>''' % \
	    (n, kw.get('attrtext', ''))

class String(TypeCode):
    '''A string type.
    '''
    parselist = [ (None,'string') ]
    seriallist = [ types.StringType, types.UnicodeType ]
    tag = 'string'

    def __init__(self, pname=None, **kw):
	TypeCode.__init__(self, pname, **kw)
	self.resolver = kw.get('resolver')
	self.strip = kw.get('strip', 1)
	self.textprotect = kw.get('textprotect', 1)

    def parse(self, elt, ps):
	self.checkname(elt, ps)
	if not elt.hasChildNodes():
	    href = _find_href(elt)
	    if not href:
		if _find_nil(elt) not in [ "true",  "1"]:
		    # No content, no HREF, not NIL:  empty string
		    return ""
		# No content, no HREF, and is NIL...
		if self.optional: return None
		raise EvaluateException('Non-optional string missing',
			ps.Backtrace(elt))
	    if href[0] != '#':
		return ps.ResolveHREF(href, self)
	    elt = ps.FindLocalHREF(href, elt)
	    self.checktype(elt, ps)
	if self.nilled(elt, ps): return None
	v = self.simple_value(elt, ps)
	if self.strip: v = v.strip()
	if self.textprotect: v = _textunprotect(v)
	return v

    def serialize(self, sw, pyobj, **kw):
	objid = '%x' % id(pyobj)
	n = kw.get('name', self.oname) or ('E' + objid)
	if type(pyobj) in _seqtypes:
	    print >>sw, '<%s%s href="%s"/>' % \
		    (n, kw.get('attrtext', ''), pyobj[0])
	    return
	if not self.unique and sw.Known(pyobj):
	    print >>sw, '<%s%s href="#%s"/>' % \
		    (n, kw.get('attrtext', ''), objid)
	    return
	if type(pyobj) == types.UnicodeType: pyobj = pyobj.encode('utf-8')
	if kw.get('typed', self.typed):
	    if self.tag and self.tag.find(':') != -1:
		tstr = ' xsi:type="%s"' % self.tag
	    else:
		tstr = ' xsi:type="xsd:%s"' % (self.tag or 'string')
	else:
	    tstr = ''
	if self.unique:
	    idstr = ''
	else:
	    idstr = ' id="%s"' % objid
	if self.textprotect: pyobj = _textprotect(pyobj)
	print >>sw, \
	    '<%s%s%s%s>%s</%s>' % \
		(n, kw.get('attrtext', ''), idstr, tstr, pyobj, n)

class URI(String):
    '''A URI.
    '''
    parselist = [ (None,'anyURI') ]
    tag = 'anyURI'

    def parse(self, elt, ps):
	val = String.parse(self, elt, ps)
	return urldecode(val)

    def serialize(self, sw, pyobj, **kw):
	String.serialize(self, sw, urlencode(pyobj), **kw)

class Base64String(String):
    '''A Base64 encoded string.
    '''
    parselist = [ (None,'base64Binary'), (SOAP.ENC, 'base64') ]
    tag = 'SOAP-ENC:base64'

    def parse(self, elt, ps):
	val = String.parse(self, elt, ps)
	return b64decode(val.replace(' ', '').replace('\n','').replace('\r',''))

    def serialize(self, sw, pyobj, **kw):
	String.serialize(self, sw, '\n' + b64encode(pyobj), **kw)

class HexBinaryString(String):
    '''Hex-encoded binary (yuk).
    '''
    parselist = [ (None,'hexBinary') ]
    tag = 'hexBinary'

    def parse(self, elt, ps):
	val = String.parse(self, elt, ps)
	return hexdecode(val)

    def serialize(self, sw, pyobj, **kw):
	String.serialize(self, sw, hexencode(pyobj).upper(), **kw)

class Enumeration(String):
    '''A string type, limited to a set of choices.
    '''

    def __init__(self, choices, pname=None, **kw):
	String.__init__(self, pname, **kw)
	t = type(choices)
	if t in _seqtypes:
	    self.choices = tuple(choices)
	elif TypeCode.typechecks:
	    raise TypeError(
		'Enumeration choices must be list or sequence, not ' + str(t))
	if TypeCode.typechecks:
	    for c in self.choices:
		if type(c) not in _stringtypes:
		    raise TypeError(
			'Enumeration choice ' + str(c) + ' is not a string')

    def parse(self, elt, ps):
	val = String.parse(self, elt, ps)
	if val not in self.choices:
	    raise EvaluateException('Value not in enumeration list',
		    ps.Backtrace(elt))
	return val


# This is outside the Integer class purely for code esthetics.
_ignored = []

class Integer(TypeCode):
    '''Common handling for all integers.
    '''

    ranges = {
        'unsignedByte':         (0, 255),
        'unsignedShort':        (0, 65535),
        'unsignedInt':          (0, 4294967295L),
        'unsignedLong':         (0, 18446744073709551615L),

        'byte':                 (-128, 127),
        'short':                (-32768, 32767),
        'int':                  (-2147483648L, 2147483647),
        'long':                 (-9223372036854775808L, 9223372036854775807L),

        'negativeInteger':      (_ignored, -1),
        'nonPositiveInteger':   (_ignored, 0),
        'nonNegativeInteger':   (0, _ignored),
        'positiveInteger':      (1, _ignored),

	'integer':		(_ignored, _ignored)
    }
    parselist = [ (None,k) for k in ranges.keys() ]
    seriallist = [ types.IntType, types.LongType ]
    tag = None

    def __init__(self, pname=None, **kw):
	TypeCode.__init__(self, pname, **kw)
	self.format = kw.get('format', '%d')

    def parse(self, elt, ps):
	(ns,type) = self.checkname(elt, ps)
	elt = self.SimpleHREF(elt, ps, 'integer')
	if not elt: return None
	tag = self.__class__.__dict__.get('tag')
	if tag:
	    if type == None:
		type = tag
	    elif tag != type:
		raise EvaluateException('Integer type mismatch; ' \
			'got %s wanted %s' % (type,tag), ps.Backtrace(elt))
	
	if self.nilled(elt, ps): return None
	v = self.simple_value(elt, ps)
	try:
	    v = int(v)
	except:
	    try:
		v = long(v)
	    except:
		raise EvaluateException('Unparseable integer',
		    ps.Backtrace(elt))
	(rmin, rmax) = Integer.ranges.get(type, (_ignored, _ignored))
	if rmin != _ignored and v < rmin:
	    raise EvaluateException('Underflow, less than ' + repr(rmin),
		    ps.Backtrace(elt))
	if rmax != _ignored and v > rmax:
	    raise EvaluateException('Overflow, greater than ' + repr(rmax),
		    ps.Backtrace(elt))
	return v

    def serialize(self, sw, pyobj, **kw):
	n = kw.get('name', self.oname) or ('E%x' % id(pyobj))
	if kw.get('typed', self.typed):
	    tstr = ' xsi:type="xsd:%s"' % (self.tag or 'integer')
	else:
	    tstr = ''
	print >>sw, '<%s%s%s>' + self.format + '</%s>' % \
		(n, kw.get('attrtext', ''), tstr, pyobj, n)

class Decimal(TypeCode):
    '''Parent class for floating-point numbers.
    '''

    parselist = [ (None,'decimal'), (None,'float'), (None,'double') ]
    seriallist = _floattypes
    tag = None
    specials = {
	'NaN': float('NaN'),
	'-NaN': float('-NaN'),
	'INF': float('INF'),
	'-INF': float('-INF'),
    }
    ranges =  {
	'float': ( 7.0064923216240861E-46,
			-3.4028234663852886E+38, 3.4028234663852886E+38 ),
	'double': ( 2.4703282292062327E-324,
			-1.7976931348623158E+308, 1.7976931348623157E+308),
    }
    zeropat = re.compile('[1-9]')

    def __init__(self, pname=None, **kw):
	TypeCode.__init__(self, pname, **kw)
	self.format = kw.get('format', '%f')

    def parse(self, elt, ps):
	(ns,type) = self.checkname(elt, ps)
	elt = self.SimpleHREF(elt, ps, 'floating-point')
	if not elt: return None
	tag = self.__class__.__dict__.get('tag')
	if tag:
	    if type == None:
		type = tag
	    elif tag != type:
		raise EvaluateException('Floating point type mismatch; ' \
			'got %s wanted %s' % (type,tag), ps.Backtrace(elt))

	if self.nilled(elt, ps): return None
	v = self.simple_value(elt, ps).lower()
	m = Decimal.specials.get(v)
	if m: return m

	try:
	    fp = float(v)
	except:
	    raise EvaluateException('Unparseable floating point number',
		    ps.Backtrace(elt))
	if str(fp) in Decimal.specials.keys():
	    raise EvaluateException('Floating point number parsed as "' + \
		    str(fp) + '"', ps.Backtrace(elt))
	if fp == 0 and Decimal.zeropat.search(v):
	    raise EvaluateException('Floating point number parsed as zero',
		    ps.Backtrace(elt))
	(rtiny, rneg, rpos) = Decimal.ranges.get(type, (None, None, None))
	if rneg and fp < 0 and fp < rneg:
	    raise EvaluateException('Negative underflow', ps.Backtrace(elt))
	if rtiny and fp > 0 and fp < rtiny:
	    raise EvaluateException('Positive underflow', ps.Backtrace(elt))
	if rpos and fp > 0 and fp > rpos:
	    raise EvaluateException('Overflow', ps.Backtrace(elt))
	return fp

    def serialize(self, sw, pyobj, **kw):
	n = kw.get('name', self.oname) or ('E%x' % id(pyobj))
	if kw.get('typed', self.typed):
	    tstr = ' xsi:type="xsd:%s"' % (self.tag or 'decimal')
	else:
	    tstr = ''
	print >>sw, '<%s%s%s>' + self.format + '</%s>' % \
		(n, kw.get('attrtext', ''), tstr, pyobj, n)

class Boolean(TypeCode):
    '''A boolean.
    '''

    parselist = [ (None,'boolean') ]

    def parse(self, elt, ps):
	self.checkname(elt, ps)
	elt = self.SimpleHREF(elt, ps, 'boolean')
	if not elt: return None
	if self.nilled(elt, ps): return None
	v = self.simple_value(elt, ps).lower()
	if v == 'false': return 0
	if v == 'true': return 1
	try:
	    v = int(v)
	except:
	    try:
		v = long(v)
	    except:
		raise EvaluateException('Unparseable boolean',
		    ps.Backtrace(elt))
	if v: return 1
	return 0

    def serialize(self, sw, pyobj, **kw):
	n = kw.get('name', self.oname) or ('E%x' % id(pyobj))
	if kw.get('typed', self.typed):
	    tstr = ' xsi:type="xsd:boolean"'
	else:
	    tstr = ''
	pyobj = (pyobj and 1) or 0
	print >>sw, '<%s%s%s>%d</%s>' % \
	    (n, kw.get('attrtext', ''), tstr, pyobj, n)


class XML(TypeCode):
    '''Opaque XML which shouldn't be parsed.
	comments -- preserve comments
	inline -- don't href/id when serializing
	resolver -- object to resolve href's
	wrapped -- put a wrapper element around it
    '''

    # Clone returned data?
    copyit = 0

    def __init__(self, pname=None, **kw):
	TypeCode.__init__(self, pname, **kw)
	self.comments = kw.get('comments', 0)
	self.inline = kw.get('inline', 0)
	self.resolver = kw.get('resolver', 0)
	self.wrapped = kw.get('wrapped', 1)
	self.copyit = kw.get('copyit', XML.copyit)

    def parse(self, elt, ps):
	if not self.wrapped:
	    return elt
	c = _child_elements(elt)
	if not c:
	    href = _find_href(elt)
	    if not href:
		if self.optional: return None
		raise EvaluateException('Embedded XML document missing',
			ps.Backtrace(elt))
	    if href[0] != '#':
		return ps.ResolveHREF(href, self)
	    elt = ps.FindLocalHREF(href, elt)
	    c = _child_elements(elt)
	if _find_encstyle(elt) != "":
	    #raise EvaluateException('Embedded XML has unknown encodingStyle',
	    #	    ps.Backtrace(elt)
	    pass
	if len(c) != 1:
	    raise EvaluateException('Embedded XML has more than one child',
		    ps.Backtrace(elt))
	if self.copyit: return c[0].cloneNode(1)
	return c[0]

    def serialize(self, sw, pyobj, **kw):
	if not self.wrapped:
	    Canonicalize(pyobj, sw, comments=self.comments)
	    return
	objid = '%x' % id(pyobj)
	n = kw.get('name', self.oname) or ('E' + objid)
	if type(pyobj) in _stringtypes:
	    print >>sw, '<%s%s href="%s"/>' % \
		    (n, kw.get('attrtext', ''), pyobj)
	elif kw.get('inline', self.inline):
	    self.cb(sw, pyobj)
	else:
	    print >>sw, '<%s%s href="#%s"/>' % \
			(n, kw.get('attrtext', ''), objid)
	    sw.AddCallback(self.cb, pyobj)

    def cb(self, sw, pyobj):
	if sw.Known(pyobj): return
	objid = '%x' % id(pyobj)
	n = self.pname or ('E' + objid)
	print >>sw, '<%s SOAP-ENC:encodingStyle="" id="%s">' % (n, objid)
	Canonicalize(pyobj, sw, comments=self.comments)
	print >>sw, '</%s>' % n

from TCnumbers import *
from TCtimes import *
from TCcompound import *
from TCapache import *

if __name__ == '__main__': print _copyright
