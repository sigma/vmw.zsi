###########################################################################
# Joshua R. Boverhof, LBNL
# See Copyright for copyright notice!
###########################################################################

# $Id $

import sys,warnings

# twisted & related imports
from zope.interface import classProvides, implements, Interface
from twisted.python import log, failure
from twisted.web.error import NoResource
from twisted.web.server import NOT_DONE_YET
import twisted.web.http
import twisted.web.resource

# ZSI imports
from ZSI import _get_element_nsuri_name, EvaluateException, ParseException
from ZSI.parse import ParsedSoap
from ZSI.writer import SoapWriter
from ZSI import fault

# WS-Address related imports
from ZSI.address import Address
from ZSI.ServiceContainer import WSActionException


# 
# Stability: Unstable
# 

class HandlerChainInterface(Interface):
    
    def processRequest(self, input, **kw):
        """returns a representation of the request, the 
        last link in the chain must return a response
        pyobj with a typecode attribute.
        Parameters:
            input --
        Keyword Parameters:
            request -- HTTPRequest instance
            resource  -- Resource instance
        """
    def processResponse(self, output, **kw):
        """returns a string representing the soap response.
        Parameters
            output --
        Keyword Parameters:
            request -- HTTPRequest instance
            resource  -- Resource instance
        """

class CallbackChainInterface(Interface):
    
    def processRequest(self, input, **kw):
        """returns a response pyobj with a typecode 
        attribute.
        Parameters:
            input --
        Keyword Parameters:
            request -- HTTPRequest instance
            resource  -- Resource instance
        """

class DataHandler:
    classProvides(HandlerChainInterface)
    readerClass = None
    writerClass = None

    @classmethod
    def processRequest(cls, input, **kw):
        return ParsedSoap(input, readerclass=cls.readerClass)

    @classmethod
    def processResponse(cls, output, **kw):
        sw = SoapWriter(outputclass=cls.writerClass)
        sw.serialize(output)
        return sw
    
    
class DefaultCallbackHandler:
    classProvides(CallbackChainInterface)

    @classmethod
    def processRequest(cls, ps, **kw):
        """invokes callback that should return a (request,response) tuple.
        representing the SOAP request and response respectively.
        ps -- ParsedSoap instance representing HTTP Body.
        request -- twisted.web.server.Request
        """
        resource = kw['resource']
        request = kw['request']
        method =  getattr(resource, 'soap_%s' %
                           _get_element_nsuri_name(ps.body_root)[-1])
                                              
        try:
            req_pyobj,rsp_pyobj = method(ps, request=request)
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
    

class WSAddressHandler:
    """General WS-Address handler.  This implementation depends on a 
    'wsAction' dictionary in the service stub which contains keys to 
    WS-Action values.  

    Implementation saves state on request response flow, so using this 
    handle is not  reliable if execution is deferred between proceesRequest 
    and processResponse.  

    TODO: sink this up with wsdl2dispatch
    TODO: reduce coupling with WSAddressCallbackHandler.
    """
    implements(HandlerChainInterface)
    
    def processRequest(self, ps, **kw):
        # TODO: Clean this up
        resource = kw['resource']

        d = getattr(resource, 'root', None)
        key = _get_element_nsuri_name(ps.body_root)
        if d is None or d.has_key(key) is False:
            raise RuntimeError,\
                'Error looking for key(%s) in root dictionary(%s)' %(key, str(d))

        self.op_name = d[key]
        self.address = address = Address()
        address.parse(ps)
        action = address.getAction()
        if not action:
            raise WSActionException('No WS-Action specified in Request')

        request = kw['request']
        http_headers = request.getAllHeaders()
        soap_action = http_headers.get('soapaction')
        if soap_action and soap_action.strip('\'"') != action:
            raise WSActionException(\
                'SOAP Action("%s") must match WS-Action("%s") if specified.'\
                %(soap_action,action)
            )
            
        # Save WS-Address in ParsedSoap instance.
        ps.address = address
        return ps
        
    def processResponse(self, sw, **kw):
        if sw is None:
            self.address = None
            return
        
        request, resource = kw['request'], kw['resource']
        if isinstance(request, twisted.web.http.Request) is False:
            raise TypeError, '%s instance expected' %http.Request
                
        d = getattr(resource, 'wsAction', None)
        key = self.op_name
        if d is None or d.has_key(key) is False:
            raise WSActionNotSpecified,\
                'Error looking for key(%s) in wsAction dictionary(%s)' %(key, str(d))

        addressRsp = Address(action=d[key])
        if request.transport.TLS == 0:
            addressRsp.setResponseFromWSAddress(\
                 self.address, 'http://%s:%d%s' %(
                 request.host.host, request.host.port, request.path)
            )
        else:
            addressRsp.setResponseFromWSAddress(\
                 self.address, 'https://%s:%d%s' %(
                 request.host.host, request.host.port, request.path)
            )
            
        addressRsp.serialize(sw, typed=False)
        self.address = None
        return sw
    

class WSAdddressCallbackHandler:
    classProvides(CallbackChainInterface)

    @classmethod
    def processRequest(cls, ps, **kw):
        """invokes callback that should return a (request,response) tuple.
        representing the SOAP request and response respectively.
        ps -- ParsedSoap instance representing HTTP Body.
        request -- twisted.web.server.Request
        """
        resource = kw['resource']
        request = kw['request']
        method =  getattr(resource, 'wsa_%s' %
                           _get_element_nsuri_name(ps.body_root)[-1])
                                              
        # TODO: grab ps.address, clean this up.
        try:
            req_pyobj,rsp_pyobj = method(ps, ps.address, request=request)
        except TypeError, ex:
            log.err(
                'ERROR: service %s is broken, method MUST return request, response'\
                    %self.__class__.__name__
            )
            raise
        except Exception, ex:
            log.err('failure when calling bound method')
            raise
        
        return rsp_pyobj


def CheckInputArgs(*interfaces):
    l = len(interfaces)
    def wrapper(func):
        def check_args(self, *args, **kw):
            for i in range(len(args)):
                if (l > i and interfaces[i].providedBy(args[i])) or type(args[i]) is interfaces[-1]:
                    continue
                raise TypeError, 'got %s, expecting %s' %(args[i], types[i])
            func(self, *args, **kw)
        return check_args
    return wrapper
            

class DefaultHandlerChain:
        
    @CheckInputArgs(CallbackChainInterface, HandlerChainInterface)
    def __init__(self, cb, *handlers):
        self.handlercb = cb
        self.handlers = handlers
        
    def processRequest(self, arg, **kw):
        for h in self.handlers:
            arg = h.processRequest(arg, **kw)
            
        return self.handlercb.processRequest(arg, **kw)
            
    def processResponse(self, arg, **kw):
        for h in self.handlers:
            arg = h.processResponse(arg, **kw)
            
        return str(arg)


class DefaultHandlerChainFactory:
    protocol = DefaultHandlerChain
    
    @classmethod
    def newInstance(cls):
        return cls.protocol(DefaultCallbackHandler, DataHandler)
    

class WSAddressHandlerChainFactory:
    protocol = DefaultHandlerChain
    
    @classmethod
    def newInstance(cls):
        return cls.protocol(WSAddressCallbackHandler, DataHandler, 
            WSAddressHandler())
    

class WSResource(twisted.web.resource.Resource, object):
    """
    class variables:
        encoding  --
        readerClass -- factory class to create reader for ParsedSoap instances.
        writerClass -- ElementProxy implementation to use for SoapWriter instances.
    """
    encoding = "UTF-8"
    factory = DefaultHandlerChainFactory

    def __init__(self):
        """
        chain -- request/response handler chain.
        """
        self.chain = self.factory.newInstance()
        twisted.web.resource.Resource.__init__(self)

    def _writeResponse(self, request, response, status=200):
        """
        request -- request message
        response --- response message
        status -- HTTP Status
        """
        request.setResponseCode(status)
        if self.encoding is not None:
            mimeType = 'text/xml; charset="%s"' % self.encoding
        else:
            mimeType = "text/xml"

        request.setHeader("Content-type", mimeType)
        request.setHeader("Content-length", str(len(response)))
        request.write(response)
        request.finish()
        return NOT_DONE_YET

    def _writeFault(self, request, ex):
        """
        request -- request message
        ex -- Exception 
        """
        response = None
        response = fault.FaultFromException(ex, False, sys.exc_info()[2]).AsSOAP()
        log.err('SOAP FAULT: %s' % response)
        return self._writeResponse(request, response, status=500)

    def render_POST(self, request):
        """Dispatch Method called by twisted render.
        request -- twisted.web.server.Request
        """
        data = request.content.read()
        try:
            pyobj = self.chain.processRequest(data, request=request, resource=self)
        except Exception, ex:
            return self._writeFault(request, ex)

        try:
            soap = self.chain.processResponse(pyobj, request=request, resource=self)
        except Exception, ex:
            return self._writeFault(request, ex)

        if soap is not None:
            return self._writeResponse(request, soap)

        request.finish()
        return NOT_DONE_YET

