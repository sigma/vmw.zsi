#! /usr/bin/env python
from ZSI import *
from ZSI import _copyright, resolvers
import sys, time, cStringIO as StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from sclasses import Testclass, OPDICT, _textprotect

config = {
    'uri': '"urn:soapinterop"',
    'ns': 'http://soapinterop.org/',
    'echons': 'http://soapinterop.org/echoheader/'
}

class InteropRequestHandler(BaseHTTPRequestHandler):
    server_version = 'ZSI/1.1 ' + BaseHTTPRequestHandler.server_version

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

    def do_POST(self):
	'''The POST command.'''
	try:
	    action = self.headers.get('soapaction', None)
	    if not action:
		raise TypeError, "SOAPAction header missing"
	    if action != config['uri']:
		raise TypeError, '''SOAPAction "%s" isn't "%s"''' \
			% (action, config['uri'])

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

	echohdr = (config['echons'], 'echoMeStringRequest')

	# Header tests.
	a = ps.WhatActorsArePresent()
	if len(a):
	    self.send_fault(FaultFromActor(a[0]))
	    return
	mu = ps.WhatMustIUnderstand()
	if echohdr in mu:
	    mu.remove(echohdr)
	if len(mu):
	    uri, localname = mu[0]
	    self.send_fault(FaultFromNotUnderstood(uri, localname))
	    return

	try:
	    # Echo?
	    echo_elts = [ h for h in ps.header_elements
			    if (h.namespaceURI, h.localName) == echohdr ]
	    i = len(echo_elts)
	    if i > 1:
		self.send_fault(Fault(Fault.Client, 'Duplicate echo header.'))
		return
	    if i == 0:
		echoval = None
	    else:
		data = TC.String(echohdr[1]).parse(h, ps)
		echoval = \
	'<E:echoMeStringResponse xmlns:E="%s">%s</E:echoMeStringResponse>\n' % \
			(echohdr[0], _textprotect(data))

	    # What operation?
	    elt = ps.body_root
	    if elt.namespaceURI != config['ns']:
		self.send_fault(Fault(Fault.Client,
			'Wrong namespace (wanted "%s" got "%s")' % \
			(config['ns'], elt.namespaceURI)))
		return
	    n = str(elt.localName)
	    if not OPDICT.has_key(n):
		self.send_fault(Fault(Fault.Client,
		    'Unknown operation "%s"' % n))
		return

	    # Do the work.
	    reply = StringIO.StringIO()
	    if n == 'echoVoidxxx':
		SoapWriter(reply, None, echoval).close()
	    else:
		try:
		    data = ps.Parse(OPDICT[n])
		except ParseException, e:
		    self.send_fault(FaultFromZSIException(e))
		self.trace(str(data), 'PARSED')
		sw = SoapWriter(reply, nsdict={ 'Z': config['ns'] }, header=echoval)
		sw.serialize(data, OPDICT[n],
			name = 'Z:' + n + 'Response', inline=1)
		sw.close()
	    self.send_xml(reply.getvalue())
	except Exception, e:
	    self.send_fault(FaultFromException(e, 0, sys.exc_info()[2]))


class QuittableHTTPServer(HTTPServer):
    def __init__(self, me, **kw):
	HTTPServer.__init__(self, me, InteropRequestHandler)
	self.quitting = 0
	self.tracefile = kw.get('tracefile', None)
    def handle_error(self, req, client_address):
	if self.quitting: sys.exit(0)
	HTTPServer.handle_error(self, req, client_address)


import getopt
try:
    (opts, args) = getopt.getopt(sys.argv[1:],
		    'l:p:t:', ( 'log=', 'port=', 'tracefile='))
except getopt.GetoptError, e:
    print >>sys.stderr, sys.argv[0] + ': ' + str(e)
    sys.exit(1)
if args:
    print sys.argv[0] + ': Usage error.'
    sys.exit(1)

portnum = 7000
tracefile = None
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
ME = ( '', portnum )

try:
    QuittableHTTPServer(ME, tracefile=tracefile).serve_forever()
except SystemExit:
    sys.exit(0)

