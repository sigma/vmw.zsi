# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

import string, httplib, smtplib, urllib, socket
from TimeoutSocket import TimeoutSocket
from TimeoutSocket import TimeoutError
from StringIO import StringIO
from urlparse import urlparse


class HTTPTransport:
    """Manages the transport of SOAP messages over the HTTP protocol."""

    def __init__(self, timeout=20, key_file=None, cert_file=None):
        self.key_file = key_file
        self.cert_file = cert_file
        self.timeout = timeout
        self.redirects = {}

    userAgent = 'Python WebService Toolkit'
    followRedirects = 1

    # This implementation maintains a cache shared by transport instances
    # that remembers redirects and demands for M-POST (if anyone uses it).
    _req_cache = {}
    
    def send(self, address, soapAction, message, contentType='text/xml',
             headers={}):
        """Send a SOAP message using HTTP, returning an HTTPResponse."""
        address, verb = self._req_cache.get(address, (address, 'POST'))

        scheme, host, path, params, query, frag = urlparse(address)
        if params: path = '%s;%s' % (path, params)
        if query:  path = '%s?%s' % (path, query)
        if frag:   path = '%s#%s' % (path, frag)

        if hasattr(message, 'getvalue'):
            body = message.getvalue()
        elif hasattr(message, 'read'):
            body = message.read()
        else: body = message

        if scheme == 'https':
            conn = TimeoutHTTPS(host, None, self.timeout,
                               key_file = self.key_file,
                               cert_file = self.cert_file
                               )
        else:
            conn = TimeoutHTTP(host, None, self.timeout)

        conn.putrequest(verb, path)

        if verb == 'M-POST':
            conn.putheader(
                'Man', '"http://schemas.xmlsoap.org/soap/envelope/"; ns=01'
                )

        for name, value in headers.items():
            conn.putheader(name, value)

        sentheader = headers.has_key

        if not sentheader('SOAPAction') or sentheader('01-SOAPAction'):
            header = verb == 'POST' and 'SOAPAction' or '01-SOAPAction'
            conn.putheader(header, soapAction)

        if not sentheader('Connection'):
            conn.putheader('Connection', 'close')

        if not sentheader('User-Agent'):
            conn.putheader('User-Agent', self.userAgent)

        if not sentheader('Content-Type'):
            conn.putheader('Content-Type', contentType)

        if not sentheader('Content-Length'):
            conn.putheader('Content-Length', str(len(body)))

        conn.endheaders()
        conn.send(body)

        response = None
        while 1:
            response = conn.getresponse()
            if response.status != 100:
                break
            conn._HTTPConnection__state = httplib._CS_REQ_SENT
            conn._HTTPConnection__response = None

        status = response.status

        # If the server only supports M-POST, we will try again using
        # the HTTP extension framework (may never happen in practice).
        if status == 510 and verb == 'POST':
            response.close()
            self._req_cache[address] = address, 'M-POST'
            return self.send(address, soapAction, message, headers)

        # If we get an HTTP redirect, we will follow it automatically.
        if status >= 300 and status < 400 and self.followRedirects:
            location = response.msg.getheader('location')
            if location is not None:
                response.close()
                if self.redirects.has_key(location):
                    raise RecursionError(
                        'Circular HTTP redirection detected.'
                        )
                self.redirects[location] = 1
                self._req_cache[address] = location, verb
                return self.send(location, soapAction, message, headers)
            raise HTTPResponse(response)

        # Otherwise, any non-2xx response may or may not not contain a
        # meaningful SOAP message. A 500 error *may* contain a message,
        # so we will raise an HTTP error unless the response is xml.
        if not (status >= 200 and status < 300):
            content_type =  response.msg.getheader('content-type', '')
            if content_type[:8] != 'text/xml':
                raise HTTPResponse(response)

        return HTTPResponse(response)


class HTTPResponse:
    """Captures the information in an HTTP response message."""

    def __init__(self, response):
        self.status = response.status
        self.reason = response.reason
        self.headers = response.msg
        self.body = response.read() or None
        response.close()


class SMTPTransport:
    """Manages the transport of SOAP messages over the SMTP protocol."""

    def __init__(self, smtphost, fromaddr, subject, timeout=20):
        self.smtphost = smtphost
        self.fromaddr = fromaddr
        self.subject = subject
        self.timeout = timeout

    def send(self, address, soapAction, message, contentType='text/xml',
             headers=None):
        """Send a SOAP message object via SMTP. Messages sent via
           SMTP are by definition one-way, so this always returns
           None on success or raises an exception from smtplib if
           an error occurs while attempting to send the message."""

        if address[:7] == 'mailto:':
            scheme, host, address, params, query, frag = urlparse(address)

        if hasattr(message, 'read'):
            message = message.read()

        smtpheaders = []
        if headers is not None:
            for name, value in headers.items():
                smtpheaders.append('%s: %s' % (name, value))
        smtpheaders.append('SOAPAction: %s' % soapAction)
        smtpheaders.append('Subject: %s' % self.subject)
        smtpheaders.append('To: <%s>' % address)

        if not headers.has_key('Content-Type'):
            smtpheaders.append('Content-Type: %s' % contentType)

        msgdata = '%s\r\n%s' % (
            string.join(smtpheaders, '\r\n'),
            message
            )
        server = TimeoutSMTP(self.smtphost, 0, self.timeout)
        server.sendmail(self.fromaddr, address, msgdata)
        server.quit()

        return None


from httplib import HTTPConnection, HTTPSConnection
from smtplib import SMTP, SMTP_PORT

class TimeoutHTTP(HTTPConnection):
    """A custom http connection object that supports socket timeout."""
    def __init__(self, host, port=None, timeout=20):
        HTTPConnection.__init__(self, host, port)
        self.timeout = timeout

    def connect(self):
        self.sock = TimeoutSocket(self.timeout)
        self.sock.connect((self.host, self.port))


class TimeoutHTTPS(HTTPSConnection):
    """A custom https object that supports socket timeout. Note that this
       is not really complete. The builtin SSL support in the Python socket
       module requires a real socket (type) to be passed in to be hooked to
       SSL. That means our fake socket won't work and our timeout hacks are
       bypassed for send and recv calls. Since our hack _is_ in place at
       connect() time, it should at least provide some timeout protection."""
    def __init__(self, host, port=None, timeout=20, **kwargs):
        if not hasattr(socket, 'ssl'):
            raise ValueError(
                'This Python installation does not have SSL support.'
                )
        HTTPSConnection.__init__(self, str(host), port, **kwargs)
        self.timeout = timeout

    def connect(self):
        sock = TimeoutSocket(self.timeout)
        sock.connect((self.host, self.port))
        realsock = getattr(sock.sock, '_sock', sock.sock)
        ssl = socket.ssl(realsock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(sock, ssl)


class TimeoutSMTP(SMTP):
    """A custom smtp object that supports socket timeout."""

    def __init__(self, host='', port=0, timeout=20):
        self.timeout = timeout
        SMTP.__init__(self, str(host), port)

    def connect(self, host='localhost', port = 0):
        if not port:
            i = host.find(':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
                try: port = int(port)
                except ValueError:
                    raise socket.error, "nonnumeric port"
        if not port: port = SMTP_PORT
        self.sock = TimeoutSocket(self.timeout)
        if self.debuglevel > 0: print 'connect:', (host, port)
        try:
            self.sock.connect((host, port))
        except socket.error:
            self.close()
            raise
        (code,msg)=self.getreply()
        if self.debuglevel >0 : print "connect:", msg
        return (code,msg)


def urlopen(url, timeout=20, redirects=None):
    """A minimal urlopen replacement hack that supports timeouts for http.
       Note that this supports GET only."""
    scheme, host, path, params, query, frag = urlparse(url)
    if not scheme in ('http', 'https'):
        return urllib.urlopen(url)
    if params: path = '%s;%s' % (path, params)
    if query:  path = '%s?%s' % (path, query)
    if frag:   path = '%s#%s' % (path, frag)

    if scheme == 'https':
        if not hasattr(socket, 'ssl'):
            raise ValueError(
                'This Python installation does not have SSL support.'
                )
        conn = TimeoutHTTPS(host, None, timeout)
    else:
        conn = TimeoutHTTP(host, None, timeout)

    conn.putrequest('GET', path)
    conn.putheader('Connection', 'close')
    conn.endheaders()
    response = None
    while 1:
        response = conn.getresponse()
        if response.status != 100:
            break
        conn._HTTPConnection__state = httplib._CS_REQ_SENT
        conn._HTTPConnection__response = None

    status = response.status

    # If we get an HTTP redirect, we will follow it automatically.
    if status >= 300 and status < 400:
        location = response.msg.getheader('location')
        if location is not None:
            response.close()
            if redirects is not None and redirects.has_key(location):
                raise RecursionError(
                    'Circular HTTP redirection detected.'
                    )
            if redirects is None:
                redirects = {}
            redirects[location] = 1
            return urlopen(location, timeout, redirects)
        raise HTTPResponse(response)

    if not (status >= 200 and status < 300):
        raise HTTPResponse(response)

    body = StringIO(response.read())
    response.close()
    return body

