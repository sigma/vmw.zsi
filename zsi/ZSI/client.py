#! /usr/bin/env python
# $Header$
#
# Copyright (c) 2001 Zolera Systems.  All rights reserved.

from ZSI import _copyright, ParsedSoap, SoapWriter, TC, ZSI_SCHEMA_URI, \
    FaultFromFaultMessage, _child_elements
from ZSI.auth import AUTH
import base64, httplib, cStringIO as StringIO, types, time

_b64_encode = base64.encodestring

_AuthHeader = '<BasicAuth xmlns="' + ZSI_SCHEMA_URI + '''">
    <Name>%s</Name><Password>%s</Password>
</BasicAuth>'''


class _Caller:
    '''Internal class used to give the user a callable object
    that calls back to the Binding object to make an RPC call.'''

    def __init__(self, binding, name):
	self.binding, self.name = binding, name

    def __call__(self, *args):
	return self.binding.RPC(None, self.name, args, TC.Any(),
		requesttypecode=TC.Any(self.name))


class Binding:
    '''Object that represents a binding (connection) to a SOAP server.
    Once the binding is created, various ways of sending and
    receiving SOAP messages are available, including a "name overloading"
    style.
    '''

    def __init__(self, **kw):
	'''Initialize.
	Keyword arguments include:
	    host, port -- where server is; defalt is localhost
	    ssl -- use SSL? default is no
	    url -- resource to POST to
	    auth -- (type, name, password) triplet; default is unauth
	    ns -- default namespace
	    nsdict -- namespace entries to add
	    tracefile -- file to dump packet traces
	    cert_file, key_file -- SSL data (q.v.)
	    uselists -- use lists, not dictionaries (default is yes)
	'''
	self.data, self.ps, self.ns, self.user_headers = \
	    None, None, None, []
	self.nsdict, self.ssl, self.url, self.trace, self.host = \
	    kw.get('nsdict', {}), kw.get('ssl', 0), kw.get('url'), \
	    kw.get('tracefile'), kw.get('host', 'localhost')
	if kw.has_key('auth'):
	    self.SetAuth(*kw['auth'])
	else:
	    self.SetAuth(AUTH.none)
	if self.nsdict.has_key(''):
	    self.SetNS(nsdict[''])
	elif kw.has_key('ns'):
	    self.SetNS(kw['ns'])
	if not self.ssl:
	    self.port = kw.get('port', httplib.HTTP_PORT)
	    self.h = httplib.HTTP()
	else:
	    self.port = kw.get('port', httplib.HTTPS_PORT)
	    x509 = {}
	    for k in [ 'cert_file', 'key_file' ]:
		if kw.has_key(k): x509[k] = kw[k]
	    self.h = httplib.HTTPS(**x509)

    def SetAuth(self, style, user=None, password=None):
	'''Change auth style, return object to user.
	'''
	self.auth_style, self.auth_user, self.auth_pass = \
	    style, user, password
	return self

    def SetNS(self, uri):
	'''Change the default namespace.
	'''
	self.ns = uri
	return self

    def SetURL(self, url):
	'''Set the URL we post to.
	'''
	self.url = url
	return self

    def ResetHeaders():
	'''Empty the list of additional headers.
	'''
	self.user_headers = []
	return self

    def AddHeader(self, header, value):
	'''Add a header to send.
	'''
	self.user_headers.append((header, value))
	return self

    def RPC(self, url, opname, obj, replyclass, **kw):
	'''Send a request, return the reply.  See Send() and Recieve()
	docstrings for details.
	'''
	self.Send(url, opname, obj, **kw)
	return self.Receive(replyclass, **kw)

    def Send(self, url, opname, obj, **kw):
	'''Send a message.  If url is None, use the value from the
	constructor (else error). obj is the object (data) to send.
	Data may be described with a requesttypecode keyword, or a
	requestclass keyword; default is the class's typecode (if
	there is one), else Any.
	'''
	# Get the TC for the obj.
	if kw.has_key('requesttypecode'):
	    tc = kw['requesttypecode']
	elif kw.has_key('requestclass'):
	    tc = kw['requestclass'].typecode
	elif type(obj) == types.InstanceType:
	    tc = obj.__class__.__dict__.get('typecode')
	    if tc == None: tc = TC.Any(opname)
	else:
	    tc = TC.Any(opname)

	# Determine the SOAP auth element.
	if self.auth_style & AUTH.zsibasic:
	    auth_header = _AuthHeader % (self.auth_user, self.auth_pass)
	else:
	    auth_header = None

	# Serialize the object.
	s = StringIO.StringIO()
	d = {}
	if self.ns: d[''] = self.ns
	d.update(kw.get('nsdict', self.nsdict) or {})
	sw = SoapWriter(s, nsdict=d, header=auth_header)
	sw.serialize(obj, tc)
	sw.close()
	soapdata = s.getvalue()

	# Tracing?
	if self.trace:
	    print >>self.trace, "_" * 33, time.ctime(time.time()), "REQUEST:"
	    print >>self.trace, soapdata

	# Send the request.
	self.h.connect(self.host, self.port)
	self.h.putrequest("POST", url or self.url)
	self.h.putheader("Content-length", "%d" % len(soapdata))
	self.h.putheader("Content-type", "text/xml; charset='utf-8'")
	self.h.putheader("SOAPAction",
	    kw.get('soapaction', '"http://www.zolera.com"'))
	if self.auth_style & AUTH.httpbasic:
	    val = _b64_encode(self.auth_user + ':' + self.auth_pass).strip()
	    self.h.putheader('Authorization', 'Basic ' + val)
	for header,value in self.user_headers:
	    self.h.putheader(header, value)
	self.h.endheaders()
	self.h.send(soapdata)

	# Clear prior receive state.
	self.data, self.ps = None, None

    def ReceiveRaw(self, **kw):
	'''Read a server reply, unconverted to any format and return it.
	'''
	if self.data: return self.data
	self.reply_code, self.reply_msg, self.reply_headers = self.h.getreply()
	self.data = self.h.getfile().read()
	if self.trace:
	    print >>self.trace, "_" * 33, time.ctime(time.time()), "RESPONSE:"
	    print >>self.trace, str(self.reply_headers)
	    print >>self.trace, self.data
	return self.data

    def IsSOAP(self):
	if self.ps: return 1
	self.ReceiveRaw()
	mimetype = self.reply_headers.type
	return mimetype == 'text/xml'

    def ReceiveSOAP(self, **kw):
	'''Get back a SOAP message.
	'''
	if self.ps: return self.ps
	if not self.IsSOAP():
	    raise TypeError(
		'Response is "%s", not "text/xml"' % self.reply_headers.type)
	if len(self.data) == 0:
	    raise TypeError('Received empty response')
	self.ps = ParsedSoap(self.data)
	return self.ps

    def IsAFault(self):
	'''Get a SOAP message, see if it has a fault.
	'''
	self.ReceiveSOAP()
	return self.ps.IsAFault()

    def ReceiveFault(self, **kw):
	'''Parse incoming message as a fault. Raise TypeError if no
	fault found.
	'''
	self.ReceiveSOAP(**kw)
	if not self.ps.IsAFault():
	    raise TypeError("Expected SOAP Fault not found")
	return FaultFromFaultMessage(self.ps)

    def Receive(self, replytype, **kw):
	'''Parse message, create Python object. if replytype is None, use
	TC.Any to dynamically parse; otherwise it can be a Python class
	or the typecode to use in parsing.
	'''
	self.ReceiveSOAP(**kw)
	if self.ps.IsAFault():
	    msg = FaultFromFaultMessage(self.ps)
	    raise TypeError("Unexpected SOAP fault: " + msg.string)
	if replytype == None:
	    tc = TC.Any()
	    data = _child_elements(self.ps.body_root)
	    if len(data) == 0: return None
	    return tc.parse(data[0], self.ps)
	elif hasattr(replytype, 'typecode'):
	    tc = replytype.typecode
	else:
	    tc = replytype
	return self.ps.Parse(tc)
	#data = _child_elements(self.ps.body_root)
	#if len(data) == 0: return None
	#return tc.parse(data[0], self.ps)

    def __repr__(self):
	return "<%s.Binding at 0x%x>" % (__name__, id(self))

    def __getattr__(self, name):
	'''Return a callable object that will invoke the RPC method
	named by the attribute.
	'''
	if name[:2] == '__' and len(name) > 5 and name[-2:] == '__':
	    if self.__dict__.has_key(name): return self._dict__[name]
	    return self.__class__.__dict__[name]
	return _Caller(self, name)

if __name__ == '__main__': print _copyright
