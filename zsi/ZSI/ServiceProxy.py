# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

import weakref, re, os, sys
from ConfigParser import SafeConfigParser as ConfigParser,\
    NoSectionError, NoOptionError
from urlparse import urlparse

from ZSI import TC
from ZSI.client import _Binding
from ZSI.generate import commands,containers
from ZSI.schema import GED, GTD

import wstools


#url_to_mod = re.compile(r'<([^ \t\n\r\f\v:]+:)?include\s+location\s*=\s*"(\S+)"')
def _urn_to_module(urn): return '%s_types' %re.sub(_urn_to_module.regex, '_', urn)
_urn_to_module.regex = re.compile(r'[\W]')
    

class ServiceProxy:
    """A ServiceProxy provides a convenient way to call a remote web
       service that is described with WSDL. The proxy exposes methods
       that reflect the methods of the remote web service."""

    def __init__(self, wsdl, url=None, service=None, port=None, tracefile=None,
                 nsdict=None, transport=None, transdict=None, 
                 cachedir='.service_proxy_dir', asdict=True):
        """
        Parameters:
           wsdl -- URL of WSDL.
           url -- override WSDL SOAP address location
           service -- service name or index
           port -- port name or index
           tracefile -- 
           nsdict -- key prefix to namespace mappings for serialization
              in SOAP Envelope.
           transport -- override default transports.
           transdict -- arguments to pass into HTTPConnection constructor.
           cachedir -- where to store generated files
           asdict -- use dicts, else use generated pyclass
        """
        self._asdict = asdict
        
        # client._Binding
        self._tracefile = tracefile
        self._nsdict = nsdict or {}
        self._transdict = transdict 
        self._transport = transport
        self._url = url
        
        # WSDL
        self._wsdl = wstools.WSDLTools.WSDLReader().loadFromURL(wsdl)
        self._service = self._wsdl.services[service or 0]
        self.__doc__ = self._service.documentation
        self._port = self._service.ports[port or 0]
        self._name = self._service.name
        self._methods = {}
        
        # Set up rpc methods for service/port
        port = self._port
        binding = port.getBinding()
        portType = binding.getPortType()
        for port in self._service.ports:
            for item in port.getPortType().operations:
                callinfo = wstools.WSDLTools.callInfoFromWSDL(port, item.name)
                method = MethodProxy(self, callinfo)
                setattr(self, item.name, method)
                self._methods.setdefault(item.name, []).append(method)
       
        # wsdl2py: deal with XML Schema
        if not os.path.isdir(cachedir): os.mkdir(cachedir)
    
        file = os.path.join(cachedir, '.cache')
        section = 'TYPES'
        cp = ConfigParser()
        try:
            cp.readfp(open(file, 'r'))
        except IOError:
            del cp;  cp = None
            
        option = wsdl.replace(':', '-') # colons seem to screw up option
        if (cp is not None and cp.has_section(section) and 
            cp.has_option(section, option)):
            types = cp.get(section, option)
        else:
            # dont do anything to anames
            containers.ContainerBase.func_aname = lambda instnc,n: str(n)
            files = commands.wsdl2py(['-o', cachedir, wsdl])
            if cp is None: cp = ConfigParser()
            if not cp.has_section(section): cp.add_section(section)

            types = filter(lambda f: f.endswith('_types.py'), files)[0]
            cp.set(section, option, types)
            cp.write(open(file, 'w'))
            
        if os.path.abspath(cachedir) not in sys.path:
            sys.path.append(os.path.abspath(cachedir))

        mod = os.path.split(types)[-1].rstrip('.py')
        self._mod = __import__(mod)
        
    def _call(self, name, *args, **kwargs):
        """Call the named remote web service method."""
        if len(args) and len(kwargs):
            raise TypeError(
                'Use positional or keyword argument only.'
                )

        callinfo = getattr(self, name).callinfo

        # go through the list of defined methods, and look for the one with
        # the same number of arguments as what was passed.  this is a weak
        # check that should probably be improved in the future to check the
        # types of the arguments to allow for polymorphism
        for method in self._methods[name]:
            if len(method.callinfo.inparams) == len(kwargs):
                callinfo = method.callinfo

        binding = _Binding(tracefile=self._tracefile,
                          url=self._url or callinfo.location, 
                          nsdict=self._nsdict, 
                          soapaction=callinfo.soapAction)


        if len(kwargs): args = kwargs

        kw = dict(unique=True)
        if callinfo.use == 'encoded':
            kw['unique'] = False

        if callinfo.style == 'rpc':
            request = TC.Struct(None, ofwhat=[], 
                             pname=(callinfo.namespace, name), **kw)
            
            response = TC.Struct(None, ofwhat=[], 
                             pname=(callinfo.namespace, name+"Response"), **kw)
            
            if len(callinfo.getInParameters()) != len(args):
                raise RuntimeError('expecting "%s" parts, got %s' %(
                       str(callinfo.getInParameters(), str(args))))
            
            for msg,pms in ((request,callinfo.getInParameters()), 
                            (response,callinfo.getOutParameters())):
                msg.ofwhat = []
                for part in pms:
                    klass = GTD(*part.type)
                    if klass is None:
                        if part.type:
                            klass = filter(lambda gt: part.type==gt.type,TC.TYPES)
                            if len(klass) == 0:
                                klass = filter(lambda gt: part.type[1]==gt.type[1],TC.TYPES)
                                if not len(klass):klass = [TC.Any]
                            if len(klass) > 1: #Enumerations, XMLString, etc
                                klass = filter(lambda i: i.__dict__.has_key('type'), klass)
                            klass = klass[0]
                        else:
                            klass = TC.Any
                
                    msg.ofwhat.append(klass(part.name))
                    
                msg.ofwhat = tuple(msg.ofwhat)
            if not args: args = {}
        else:
            # Grab <part element> attribute
            ipart,opart = callinfo.getInParameters(),callinfo.getOutParameters()
            if ( len(ipart) != 1 or not ipart[0].element_type or 
                ipart[0].type is None ):
                raise RuntimeError, 'Bad Input Message "%s"' %callinfo.name
    
            if ( len(opart) not in (0,1) or not opart[0].element_type or 
                opart[0].type is None ):
                raise RuntimeError, 'Bad Output Message "%s"' %callinfo.name
            
            if ( len(args) != 1 ):
                raise RuntimeError, 'Message has only one part'
            
            ipart = ipart[0]
            request,response = GED(*ipart.type),None
            if opart: response = GED(*opart[0].type)

        if self._asdict: self._nullpyclass(request)
        binding.Send(None, None, args,
                     requesttypecode=request,
                     encodingStyle=callinfo.encodingStyle)
        
        if response is None: 
            return None
        
        if self._asdict: self._nullpyclass(response)
        return binding.Receive(replytype=response,
                     encodingStyle=callinfo.encodingStyle)

    def _nullpyclass(cls, typecode):
        typecode.pyclass = None
        if not hasattr(typecode, 'ofwhat'): return
        if type(typecode.ofwhat) not in (list,tuple): #Array
            cls._nullpyclass(typecode.ofwhat)
        else: #Struct/ComplexType
            for i in typecode.ofwhat: cls._nullpyclass(i)    
    _nullpyclass = classmethod(_nullpyclass)


class MethodProxy:
    """ """
    def __init__(self, parent, callinfo):
        self.__name__ = callinfo.methodName
        self.__doc__ = callinfo.documentation
        self.callinfo = callinfo
        self.parent = weakref.ref(parent)

    def __call__(self, *args, **kwargs):
        return self.parent()._call(self.__name__, *args, **kwargs)
