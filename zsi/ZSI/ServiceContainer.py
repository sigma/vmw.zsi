#! /usr/bin/env python
'''Simple Service Container
   -- use with wsdl2py generated modules.
'''

import urlparse, types, os, sys, cStringIO as StringIO
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from ZSI import ParseException, FaultFromException
from ZSI import _copyright, _seqtypes, resolvers
from ZSI.parse import ParsedSoap
from ZSI.writer import SoapWriter
from ZSI.dispatch import _ModPythonSendXML, _ModPythonSendFault, _CGISendXML, _CGISendFault
from ZSI.dispatch import SOAPRequestHandler as BaseSOAPRequestHandler

"""
Functions:
    _Dispatch
    AsServer

Classes:
    NoSuchService
    PostNotSpecified
    SOAPActionNotSpecified
    ServiceSOAPBinding
    SOAPRequestHandler
    ServiceContainer
"""

def _Dispatch(ps, server, SendResponse, SendFault, post, action, nsdict={}, **kw):
    '''Send ParsedSoap instance to ServiceContainer, which dispatches to
    appropriate service via post, and method via action.  Response is a
    self-describing pyobj, which is passed to a SoapWriter.

    Call SendResponse or SendFault to send the reply back, appropriately.
        server -- ServiceContainer instance

    '''
    try:
        result = server(ps, post, action)
    except Exception, e:
        return SendFault(FaultFromException(e, 0, sys.exc_info()[2]), **kw)
    if result == None:
        return
    reply = StringIO.StringIO()
    try:
        SoapWriter(reply, nsdict=nsdict).serialize(result)
        return SendResponse(reply.getvalue(), **kw)
    except Exception, e:
        return SendFault(FaultFromException(e, 0, sys.exc_info()[2]), **kw)


def AsServer(port=80, services=()):
    '''port --
       services -- list of service instances
    '''
    address = ('', port)
    sc = ServiceContainer(address)
    for service in services:
        path = service.getPost()
        sc.setNode(service, path)
    sc.serve_forever()


class NoSuchService(Exception): pass
class NoSuchMethod(Exception): pass
class NotAuthorized(Exception): pass
class ServiceAlreadyPresent(Exception): pass
class PostNotSpecified(Exception): pass
class SOAPActionNotSpecified(Exception): pass

class ServiceSOAPBinding:
    """
    Binding defines the set of wsdl:binding operations, it takes as input
    a ParsedSoap instance and parses it into a pyobj.  It returns a
    response pyobj.
 
    class variables:
        soapAction -- dictionary of soapAction keys, and operation name values.
           These are specified in the WSDL soap bindings. There must be a 
           class method matching the operation name value.

    """
    soapAction = {}
    
    def __init__(self, post):
        self.post = post

    def authorize(self, auth_info, post, action):
        return 1

    def __call___(self, action, ps):
        return self.getOperation(action)(ps)

    def getPost(self):
        return self.post

    def getOperation(self, action):
        '''Returns a method of class.
           action -- soapAction value
        '''
        opName = self.getOperationName(action)
        return getattr(self, opName)

    def getOperationName(self, action):
        '''Returns operation name.
           action -- soapAction value
        '''
        if not self.soapAction.has_key(action):
            raise SOAPActionNotSpecified, '%s is NOT in soapAction dictionary' %action
        return self.soapAction[action]


class SOAPRequestHandler(BaseSOAPRequestHandler):
    '''SOAP handler.
    '''
    def do_POST(self):
        '''The POST command.
        '''
        soapAction = self.headers.getheader('SOAPAction').strip('\'"')
        post = self.path
        if not post:
            raise PostNotSpecified, 'HTTP POST not specified in request'
        if not soapAction:
            raise SOAPActionNotSpecified, 'SOAP Action not specified in request'
        soapAction = soapAction.strip('\'"')
        post = post.strip('\'"')
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
        except Exception, e:
            # Faulted while processing; assume it's in the header.
            self.send_fault(FaultFromException(e, 1, sys.exc_info()[2]))
        else:
            _Dispatch(ps, self.server, self.send_xml, self.send_fault, 
                post=post, action=soapAction)


class ServiceContainer(HTTPServer):
    '''HTTPServer that stores service instances according 
    to POST values.  An action value is instance specific,
    and specifies an operation (function) of an instance.
    '''
    class NodeTree:
        '''Simple dictionary implementation of a node tree
        '''
        def __init__(self):
            self.__dict = {}

        def __str__(self):
            return str(self.__dict)

        def getNode(self, url):
            path = urlparse.urlsplit(url)[2]

            if self.__dict.has_key(path):                

                return self.__dict[path]
            else:
                raise NoSuchService, 'No service(%s) in ServiceContainer' %path
            
        def setNode(self, service, url):
            if not isinstance(service, ServiceSOAPBinding):
               raise TypeError, 'A Service must implement class ServiceSOAPBinding'
            path = urlparse.urlsplit(url)[2]
            
            if self.__dict.has_key(path):
                raise ServiceAlreadyPresent, 'Service(%s) already in ServiceContainer' % path
            else:
                self.__dict[path] = service

        def removeNode(self, url):
            path = urlparse.urlsplit(url)[2]

            if self.__dict.has_key(path):
                node = self.__dict[path]
                del self.__dict[path]
                return node
            else:
                raise NoSuchService, 'No service(%s) in ServiceContainer' %path
            
    def __init__(self, server_address, RequestHandlerClass=SOAPRequestHandler):
        '''server_address -- 
           RequestHandlerClass -- 
        '''
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self._nodes = self.NodeTree()

    def __call__(self, ps, post, action):
        '''ps -- ParsedSoap representing the request
           post -- HTTP POST --> instance
           action -- Soap Action header --> method
        '''
        return self.getCallBack(post, action)(ps)

    def getNode(self, post):
        '''post -- POST HTTP value
        '''
        return self._nodes.getNode(post)

    def setNode(self, service, post):
        '''service -- service instance
           post -- POST HTTP value
        '''
        self._nodes.setNode(service, post)

    def removeNode(self, post):
        '''post -- POST HTTP value
        '''
        self._nodes.removeNode(post)
        
    def getCallBack(self, post, action):
        '''post -- POST HTTP value
           action -- SOAP Action value
        '''
        node = self.getNode(post)
        
        if node is None:
            raise NoSuchMethod, "Method (%s) not found at path (%s)" % (action,
                                                                        path)

        if node.authorize(None, post, action):
            return node.getOperation(action)
        else:
            raise NotAuthorized, "Authorization failed for method %s" % action

if __name__ == '__main__': print _copyright
