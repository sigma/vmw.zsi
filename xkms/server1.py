#! /usr/bin/env python2

import os, sys
from BaseHTTPServer import BaseHTTPRequestHandler
from ZSI import *
from M2Crypto import Rand, SSL
from M2Crypto.SSL.SSLServer import SSLServer

XKMS_NSURI = '...'

class XKMSRequestHandler(BaseHTTPRequestHandler):
    server_version = 'ZSI/1.4 XKMS/1.0 '+ BaseHTTPRequestHandler.server_version

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

    def do_GET(self):
        self.send_response(301)
        self.send_header('Content-type', 'text/html');
        self.send_header('Location', 'http://webservices.xml.com')
        self.trace('<<GET>>', 'GOT GET')
        self.end_headers()

    def do_POST(self):
        try:
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

        try:
            # Is the operation defined?
            root = ps.body_root
            n = root.localName
            if n not in ['Register','Revoke']:
                self.send_fault(Fault(Fault.Client,
                    'Unknown operation "%s"' % n))
                return

            if root.namespaceURI != XKMS_NSURI:
                self.send_fault(Fault(Fault.Client,
                    'Unknown namespace "%s"' % root.namespaceURI))
                return

            nsdict = {}
            reply = StringIO.StringIO()
            sw = SoapWriter(reply, nsdict=nsdict)
            # XXX
            sw.close()
            self.send_xml(reply.getvalue())
        except Exception, e:
            # Fault while processing; now it's in the body.
            self.send_fault(FaultFromException(e, 0, sys.exc_info()[2]))
            return


class HTTPS_Server(SSLServer):
    def __init__(self, ME, HandlerClass, sslctx):
        SSLServer.__init__(self, ME, HandlerClass, sslctx)
        self.tracefile = None

    def finish(self):
        self.request.set_shutdown(SSL.SSL_RECEIVED_SHUTDOWN | SSL.SSL_SENT_SHUTDOWN)
        self.request.close()

def init_ssl_context(dir, debug=None):
    ctx = SSL.Context('sslv23')
    if debug: ctx.set_info_callback()
    ctx.load_cert(certfile=dir+'/cert.pem', keyfile=dir+'/plainkey.pem')
    ctx.set_verify(SSL.verify_none, 1)
    ctx.set_allow_unknown_ca(1)
    ctx.set_session_id_ctx('xkms_srv')
    return ctx

dir = os.environ.get('XKMSHOME', '/opt/xkms') + '/openssl/ssl'
randfile = dir + '/xkms-ca/.rand'
Rand.load_file(randfile, -1)
sslctx = init_ssl_context(dir, 1)
s = HTTPS_Server(('', 9999), XKMSRequestHandler, sslctx)
s.tracefile=sys.stderr
try:
    s.serve_forever()
except KeyboardInterrupt:
    print "Quitting..."
    pass
Rand.save_file(randfile)
