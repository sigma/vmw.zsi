#! /usr/bin/env python
# $Header$
'''Simple CGI dispatching.
'''

import os, sys, cStringIO as StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from ZSI import *
from ZSI import _child_elements, _copyright, _seqtypes, resolvers
from ZSI.auth import AUTH, ClientBinding

# Typecode to parse a ZSI BasicAuth header.
_auth_tc = TC.Struct(None,
			[ TC.String('Name'), TC.String('Password') ],
			extras=1)


# Client binding information is stored in a global. We provide an accessor
# in case later on it's not.
_client_binding = None

def GetClientBinding():
    '''Return the client binding object.
    '''
    return _client_binding

def _Dispatch(ps, modules, SendResponse, SendFault):
    '''Find a handler for the SOAP request in ps; search modules.
    Call SendResponse or SendFault to send the reply back, appropriately.
    '''
    global _client_binding
    try:
	what = ps.body_root.localName

	# See what modules have the element name.
	if modules == None:
	    modules = ( sys.modules['__main__'], )
	handlers = [ getattr(m, what) for m in modules if hasattr(m, what) ]
	if len(handlers) == 0:
	    raise TypeError("Unknown method " + what)

	# Of those modules, see who's callable.
	handlers = [ h for h in handlers if callable(h) ]
	if len(handlers) == 0:
	    raise TypeError("Unimplemented method " + what)
	if len(handlers) > 1:
	    raise TypeError("Multiple implementations found: " + `handlers`)
	handler = handlers[0]

	_client_binding = ClientBinding(ps)
	data = _child_elements(ps.body_root)
	if len(data) == 0:
	    arg = []
	else:
	    try:
		tc = TC.Any()
		arg = [ tc.parse(e, ps) for e in data ]
	    except EvaluateError, e:
		SendFault(FaultFromZSIException(e))
		return

	result = [ handler(*arg) or [] ]
	reply = StringIO.StringIO()
	SoapWriter(reply).serialize(result,
	    TC.Any(aslist=1, pname=what + 'Response')
	)
	SendResponse(reply.getvalue())
	return
    except Exception, e:
	# Something went wrong, send a fault.
	SendFault(FaultFromException(e, 0, sys.exc_info()[2]))


def _CGISendXML(text, code=200):
    print 'Status: %d' % code
    print 'Content-Type: text/xml; charset="utf-8"'
    print 'Content-Length: %d' % len(text)
    print ''
    print text

def _CGISendFault(f):
    _CGISendXML(f.AsSOAP(), 500)

def AsCGI(modules=None):
    '''Dispatch within a CGI script.
    '''
    if os.environ.get('REQUEST_METHOD', None) != 'POST':
	_CGISendFault(Fault(Fault.Client, 'Must use POST'))
	return
    ct = os.environ['CONTENT_TYPE']
    try:
	if ct.startswith('multipart/'):
	    cid = resolvers.MIMEResolver(ct, self.stdin)
	    xml = cid.GetSOAPPart()
	    ps = ParsedSoap(xml, resolver=cid.Resolve)
	else:
	    length = int(os.environ['CONTENT_LENGTH'])
	    ps = ParsedSoap(sys.stdin.read(length))
    except ParseException, e:
	_CGISendFault(FaultFromZSIException(e))
	return
    _Dispatch(ps, modules, _CGISendXML, _CGISendFault)


class SOAPRequestHandler(BaseHTTPRequestHandler):
    '''SOAP handler.
    '''
    server_version = 'ZSI/1.1 ' + BaseHTTPRequestHandler.server_version

    def send_xml(self, text, code=200):
        '''Send some XML.
	'''
	self.send_response(code)
	self.send_header('Content-type', 'text/xml; charset="utf-8"')
	self.send_header('Content-Length', str(len(text)))
	self.end_headers()
	self.wfile.write(text)
	self.wfile.flush()

    def send_fault(self, f):
	'''Send a fault.
	'''
	self.send_xml(f.AsSOAP(), 500)

    def do_POST(self):
	'''The POST command.
	'''
	try:
	    ct = self.headers['content-type']
	    if ct.startswith('multipart/'):
		cid = resolvers.MIMEResolver(ct, self.rfile)
		xml = cid.GetSOAPPart()
		ps = ParsedSoap(xml, resolver=cid.Resolve)
	    else:
		length = int(self.headers['content-length'])
		ps = ParsedSoap(self.rfile.read(length))
	except ParseException, e:
	    self.send_fault(FaultFromZSIException(e))
	    return
	except Exception, e:
	    # Faulted while processing; assume it's in the header.
	    self.send_fault(FaultFromException(e, 1, sys.exc_info()[2]))
	    return

	_Dispatch(ps, self.server.modules, self.send_xml, self.send_fault)

def AsServer(**kw):
    address = ('', kw.get('port', 80))
    httpd = HTTPServer(address, SOAPRequestHandler)
    httpd.modules = kw.get('modules', None)
    httpd.serve_forever()

if __name__ == '__main__': print _copyright
