#! /usr/bin/env python
from ZSI import *
from ZSI import _copyright, resolvers, _child_elements
import sys, time, cStringIO as StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from sclasses import Operation, WSDL_DEFINITION

config = {
    'echons': 'http://soapinterop.org/echoheader/'
}

class InteropRequestHandler(BaseHTTPRequestHandler):
    server_version = 'ZSI/1.2 ' + BaseHTTPRequestHandler.server_version

    def send_xml(self, text, code=200):
	'''Send some XML.'''
	self.send_response(code)
	self.send_header('Content-type', 'text/xml; charset="utf-8"')
	self.send_header('Content-Length', str(len(text)))
	self.end_headers()
	self.wfile.write(text)
	self.trace(text, 'SENT')
	self.wfile.flush()

    def send_fault(self, f):
	'''Send a fault.'''
	self.send_xml(f.AsSOAP(), 500)

    def trace(self, text, what):
	'''Log a debug/trace message.'''
	F = self.server.tracefile
	if not F: return
	print >>F, '=' * 60, '\n%s %s %s %s:' % \
	    (what, self.client_address, self.path, time.ctime(time.time()))
	print >>F, text
	print >>F, '=' * 60, '\n'
	F.flush()

    def do_QUIT(self):
	'''Quit.'''
	self.server.quitting = 1
	self.log_message('Got QUIT command')
	sys.stderr.flush()
	raise SystemExit

    def do_GET(self):
	'''The GET command.  Always returns the WSDL.'''
	self.send_xml(WSDL_DEFINITION.replace('>>>URL<<<', self.server.url))

    def do_POST(self):
	'''The POST command.'''

	# SOAPAction header.
	action = self.headers.get('soapaction', None)
	if not action:
	    self.send_fault(Fault(Fault.Client,
				'SOAPAction HTTP header missing.'))
	    return
	if action != Operation.SOAPAction:
	    self.send_fault(Fault(Fault.Client,
		'SOAPAction is "%s" not "%s"' % \
		(action, Operation.SOAPAction)))
	    return

	# Parse the message.
	try:
	    ct = self.headers['content-type']
	    if ct.startswith('multipart/'):
		cid = resolvers.MIMEResolver(ct, self.rfile)
		xml = cid.GetSOAPPart()
		ps = ParsedSoap(xml, resolver=cid.Resolve)
	    else:
		cl = int(self.headers['content-length'])
		IN = self.rfile.read(cl)
		self.trace(IN, 'RECEIVED')
		ps = ParsedSoap(IN)
	except ParseException, e:
	    self.send_fault(FaultFromZSIException(e))
	    return
	except Exception, e:
	    # Faulted while processing; assume it's in the header.
	    self.send_fault(FaultFromException(e, 1, sys.exc_info()[2]))
	    return

	# Actors?
	a = ps.WhatActorsArePresent()
	if len(a):
	    self.send_fault(FaultFromActor(a[0]))
	    return

	# Is the operation defined?
	elt = ps.body_root
	if elt.namespaceURI != Operation.ns:
	    self.send_fault(Fault(Fault.Client,
		'Incorrect namespace "%s"' % elt.namespaceURI))
	    return
	n = elt.localName
	op = Operation.dispatch.get(n, None)
	if not op:
	    self.send_fault(Fault(Fault.Client,
		'Undefined operation "%s"' % n))
	    return

	# Any headers that must be understood that we don't understand?
	for mu in ps.WhatMustIUnderstand():
	    if mu not in op.headers:
		uri, localname = mu[0]
		self.send_fault(FaultFromNotUnderstood(uri, localname))
		return

	# Get all headers intended for us, ignore ones we don't
	# understand since we don't have to understand them.
	# Understand? :)
	headers = [ e for e in ps.GetMyHeaderElements()
		    if (e.namespaceURI, e.localName) in op.headers ]
	if headers: self.process_headers(headers)

	try:
	    try:
		results = op.TCin.parse(ps.body_root, ps)
	    except ParseException, e:
		self.send_fault(FaultFromZSIException(e))
	    self.trace(str(results), 'PARSED')
	    reply = StringIO.StringIO()
	    sw = SoapWriter(reply, nsdict={ 'Z': Operation.ns })
	    sw.serialize(results, op.TCout,
		    name = 'Z:' + n + 'Response', inline=1)
	    sw.close()
	    self.send_xml(reply.getvalue())
	except Exception, e:
	    self.send_fault(FaultFromException(e, 0, sys.exc_info()[2]))


class InteropHTTPServer(HTTPServer):
    def __init__(self, me, url, **kw):
	HTTPServer.__init__(self, me, InteropRequestHandler)
	self.quitting = 0
	self.tracefile = kw.get('tracefile', None)
	self.url = url
    def handle_error(self, req, client_address):
	if self.quitting: sys.exit(0)
	HTTPServer.handle_error(self, req, client_address)


import getopt
try:
    (opts, args) = getopt.getopt(sys.argv[1:],
		    'l:p:t:u:', ( 'log=', 'port=', 'tracefile=', 'url='))
except getopt.GetoptError, e:
    print >>sys.stderr, sys.argv[0] + ': ' + str(e)
    sys.exit(1)
if args:
    print sys.argv[0] + ': Usage error.'
    sys.exit(1)

portnum = 1122
tracefile = None
url = None
for opt, val in opts:
    if opt in [ '-l', '--logfile' ]:
	sys.stderr = open(val, 'a')
    elif opt in [ '-p', '--port' ]:
	portnum = int(val)
    elif opt in [ '-t', '--tracefile' ]:
	if val == '-':
	    tracefile = sys.stdout
	else:
	    tracefile = open(val, 'a')
    elif opt in [ '-u', '--url' ]:
	url = val
ME = ( '', portnum )

if not url:
    import socket
    url = 'http://' + socket.getfqdn()
    if portnum != 80: url += ':%d' % portnum
    url += '/interop'

try:
    InteropHTTPServer(ME, url, tracefile=tracefile).serve_forever()
except SystemExit:
    pass
sys.exit(0)
