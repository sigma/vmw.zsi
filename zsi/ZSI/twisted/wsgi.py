############################################################################
# Joshua R. Boverhof, LBNL
# See Copyright for copyright notice!
# $Id: __init__.py 1132 2006-02-17 01:55:41Z boverhof $
###########################################################################
import os, sys, warnings
from StringIO import StringIO

# twisted & related imports
from zope.interface import classProvides, implements, Interface
from twisted.python import log, failure
#from twisted.web.error import NoResource
#from twisted.web.server import NOT_DONE_YET
#import twisted.web.http
#import twisted.web.resource

# ZSI imports
from ZSI import _get_element_nsuri_name, EvaluateException, ParseException
from ZSI import fault, ParsedSoap, SoapWriter


# WS-Address related imports
from ZSI.address import Address


class WSAddressException(Exception):
    """
    """

from ZSI.twisted.interfaces import HandlerChainInterface, CallbackChainInterface,\
    DataHandler, CheckInputArgs, DefaultHandlerChain

    
    
class DefaultCallbackHandler:
    classProvides(CallbackChainInterface)

    @classmethod
    def processRequest(cls, ps, **kw):
        """invokes callback that should return a (request,response) tuple.
        representing the SOAP request and response respectively.
        ps -- ParsedSoap instance representing HTTP Body.
        request -- twisted.web.server.Request
        """
        #env = kw['env']
        #start_response = kw['start_response']
        resource = kw['resource']
        #request = kw['request']
        method =  getattr(resource, 'soap_%s' %
                           _get_element_nsuri_name(ps.body_root)[-1])
                                              
        try:
            req_pyobj,rsp_pyobj = method(ps)
        except TypeError, ex:
            log.err(
                'ERROR: service %s is broken, method MUST return request, response'\
                    % cls.__name__
            )
            raise
        except Exception, ex:
            log.err('failure when calling bound method')
            raise
        
        return rsp_pyobj
    
    
class DefaultHandlerChainFactory:
    protocol = DefaultHandlerChain
    
    @classmethod
    def newInstance(cls):
        return cls.protocol(DefaultCallbackHandler, DataHandler)
    


class WSGIApplication(dict):
    encoding = "UTF-8"
    
    def __call__(self, env, start_response):
        """do dispatching, else process
        """
        script = env['SCRIPT_NAME'] # consumed
        ipath = os.path.split(env['PATH_INFO'])[1:]
        for i in range(1, len(ipath)+1):
            path = os.path.join(*ipath[:i])
            print "PATH: ", path
            application = self.get(path)
            if application is not None:
                env['SCRIPT_NAME'] = script + path
                env['PATH_INFO'] =  ''
                print "SCRIPT: ", env['SCRIPT_NAME']
                return application(env, start_response)
            
        return self._request_cb(env, start_response)

    def _request_cb(self, env, start_response):
        """callback method, override
        """
        start_response("404 ERROR", [('Content-Type','text/plain')])
        return ['Move along people, there is nothing to see to hear']


class SOAPApplication(WSGIApplication):
    """
    """
    factory = DefaultHandlerChainFactory
    soapAction = {}
    root = {}
    
    def __init__(self, **kw):
        dict.__init__(self, **kw)
        self.delegate = None
        
    def _request_cb(self, env, start_response):
        """process request, 
        """
        if env['REQUEST_METHOD'] == 'GET':
            return self._handle_GET(env, start_response)

        if env['REQUEST_METHOD'] == 'POST':
            return self._handle_POST(env, start_response)
            
        start_response("500 ERROR", [('Content-Type','text/plain')])
        s = StringIO()
        h = env.items(); h.sort()
        for k,v in h:
            print >>s, k,'=',`v`
        return [s.getvalue()]

    def _handle_GET(self, env, start_response):
        if env['QUERY_STRING'].lower() == 'wsdl':
            start_response("200 OK", [('Content-Type','text/plain')])
            return ['NO WSDL YET']

        start_response("404 ERROR", [('Content-Type','text/plain')])
        return ['NO RESOURCE FOR GET']
    
    def _handle_POST(self, env, start_response):
        """Dispatch Method called by twisted render, creates a
        request/response handler chain.
        request -- twisted.web.server.Request
        """
        input = env['wsgi.input']
        data = input.read( int(env['CONTENT_LENGTH']) )
        mimeType = "text/xml"
        if self.encoding is not None:
            mimeType = 'text/xml; charset="%s"' % self.encoding

        request = None
        resource = self.delegate or self
        chain = self.factory.newInstance()
        try:
            pyobj = chain.processRequest(data, request=request, resource=resource)
        except Exception, ex:
            start_response("500 ERROR", [('Content-Type',mimeType)])
            return [fault.FaultFromException(ex, False, sys.exc_info()[2]).AsSOAP()]

        try:
            soap = chain.processResponse(pyobj, request=request, resource=resource)
        except Exception, ex:
            start_response("500 ERROR", [('Content-Type',mimeType)])
            return [fault.FaultFromException(ex, False, sys.exc_info()[2]).AsSOAP()]
        
        start_response("200 OK", [('Content-Type',mimeType)])
        return [soap]
    
    
def test(app, port=8080, host="localhost"):
    """
    """
    import sys
    from twisted.internet import reactor
    from twisted.python import log
    from twisted.web2.channel import HTTPFactory
    from twisted.web2.server import Site
    from twisted.web2.wsgi import WSGIResource
    
    log.startLogging(sys.stdout)
    reactor.listenTCP(port, 
        HTTPFactory( Site(WSGIResource(app)) ),
        interface=host,
    )
    reactor.run()



